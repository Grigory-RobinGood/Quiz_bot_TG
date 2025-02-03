import asyncio
import logging
import random

from typing import Optional
from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.filters import StateFilter
from aiogram.types import CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from db.db_functions import update_user_balance
from db.models import Users
from keyboards.keyboards import main_kb
from middleware.game_mdwr import CallbackQueryMiddleware
from services.FSM import ProcessGameState

from services.game import send_next_question, SCORE_TABLE

logger = logging.getLogger(__name__)
router = Router()
# Инициализация middleware
callback_query_middleware = CallbackQueryMiddleware()
router.callback_query.middleware(callback_query_middleware)


@router.callback_query(F.data.startswith("answer:"), StateFilter(ProcessGameState.waiting_for_answer))
async def process_answer(callback: CallbackQuery, state: FSMContext, session: AsyncSession):
    data = await state.get_data()
    current_question = data["current_question"]
    correct_answer = current_question["correct_answer"]
    answers = data["answers"]

    # ✅ Получаем индекс текущего вопроса (важно!)
    question_index = data.get("question_index", 0)

    try:
        answer_index = int(callback.data.split(":")[2])
        selected_answer = answers[answer_index]

        if selected_answer == correct_answer:
            # ✅ Присваиваем баллы за текущий вопрос
            current_score = SCORE_TABLE[question_index] if question_index < len(SCORE_TABLE) else 0

            # ✅ Обновляем состояние с новым количеством баллов
            await state.update_data(current_score=current_score, question_index=question_index + 1)

            await callback.message.edit_text(f"Правильно! Ваши баллы: {current_score}")

            # Отправляем следующий вопрос
            await send_next_question(callback.message.answer, state)
        else:
            # ✅ Проверяем страховку
            hints_used = data.get("hints_used", {})
            guaranteed_score = data.get("guaranteed_score", 0)

            if hints_used.get("insure"):
                final_score = guaranteed_score
                await callback.message.edit_text(
                    f"Неправильно. Правильный ответ: {correct_answer}. "
                    f"Вы застраховали сумму: {final_score}!"
                )
                await update_user_balance(callback.from_user.id, final_score, "silver", session)
            else:
                final_score = 0
                await callback.message.edit_text(
                    f"Неправильно. Правильный ответ: {correct_answer}. Ваш выигрыш: {final_score}.")

            await state.clear()  # Завершаем игру

    except (ValueError, IndexError) as e:
        logger.error(f"Ошибка при обработке ответа: {e}")
        await callback.message.answer("Произошла ошибка. Попробуйте снова.")


async def wait_for_callback_query(user_id: int) -> Optional[CallbackQuery]:
    """
    Ожидает callback_query от конкретного пользователя.

    Args:
        user_id (int): ID пользователя, от которого ожидается callback_query.

    Returns:
        CallbackQuery: Объект callback_query от пользователя.
    """
    future = asyncio.get_event_loop().create_future()
    callback_query_middleware.user_futures[user_id] = future

    try:
        return await asyncio.wait_for(future, timeout=60)  # Таймаут 60 секунд
    except asyncio.TimeoutError:
        return None
    finally:
        await callback_query_middleware.user_futures.pop(user_id, None)


#______________Обработчики подсказок_______________________________
@router.callback_query(F.data == "hint:hint_insure", StateFilter(ProcessGameState.waiting_for_answer))
async def hint_insure(callback: CallbackQuery, state: FSMContext):
    """Обработчик кнопки 'Застраховать сумму'."""
    data = await state.get_data()

    if data["hints_used"]["insure"]:
        await callback.answer("Вы уже использовали эту подсказку!", show_alert=True)
        return

    # Фиксируем текущий выигрыш
    guaranteed_score = data["current_score"]
    data["hints_used"]["insure"] = True

    await state.update_data(hints_used=data["hints_used"], guaranteed_score=guaranteed_score)
    await callback.answer(f"Сумма застрахована: {guaranteed_score} баллов!")


@router.callback_query(F.data == "hint:hint_remove_two", StateFilter(ProcessGameState.waiting_for_answer))
async def hint_remove_two(callback: CallbackQuery, state: FSMContext):
    """Обработчик кнопки 'Убрать два неправильных ответа'."""
    data = await state.get_data()

    if data["hints_used"]["remove_two"]:
        await callback.answer("Вы уже использовали эту подсказку!", show_alert=True)
        return

    current_question = data["current_question"]
    correct_answer = current_question["correct_answer"]
    all_answers = data["answers"]  # Это список из 4-х ответов в текущем вопросе

    # Определяем индексы всех неправильных ответов
    incorrect_indices = [i for i, ans in enumerate(all_answers) if ans != correct_answer]

    # Выбираем два случайных неправильных ответа
    removed_indices = random.sample(incorrect_indices, 2)

    # Оставляем только правильный и один случайный неправильный ответ
    remaining_indices = [i for i in range(4) if i not in removed_indices]

    # Создаём новую клавиатуру только с оставшимися вариантами
    answer_buttons = [
        InlineKeyboardButton(text=chr(65 + i), callback_data=f"answer:{current_question['id']}:{i}")
        for i in remaining_indices
    ]
    keyboard = InlineKeyboardMarkup(inline_keyboard=[answer_buttons])

    # Обновляем состояние, чтобы обработчик ответов знал, какие варианты остались
    data["hints_used"]["remove_two"] = True
    await state.update_data(hints_used=data["hints_used"], remaining_indices=remaining_indices)

    # Обновляем сообщение с урезанными вариантами
    filtered_answers = [all_answers[i] for i in remaining_indices]
    formatted_answers = "\n".join(
        [f"{chr(65 + idx)}) {ans}" for idx, ans in zip(remaining_indices, filtered_answers)]
    )

    await callback.message.edit_text(
        f"Вопрос: {current_question['question_text']}\n\n{formatted_answers}",
        reply_markup=keyboard
    )
    await callback.answer("Удалены два неверных ответа!")



@router.callback_query(F.data == "hint:hint_take_money", StateFilter(ProcessGameState.waiting_for_answer))
async def hint_take_money(callback: CallbackQuery, state: FSMContext, session: AsyncSession):
    """Обработчик кнопки 'Забрать выигрыш'."""
    data = await state.get_data()
    user_id = callback.from_user.id
    current_score = data["current_score"]

    # Обновляем баланс пользователя
    result = await session.execute(select(Users).where(Users.user_id == user_id))
    user = result.scalars().first()

    if not user:
        await callback.answer("Ошибка: пользователь не найден!", show_alert=True)
        return

    user.balance_silver += current_score
    await session.commit()

    await callback.message.edit_text(f"Игра завершена! Вы забрали {current_score} баллов.", reply_markup=main_kb)
    await state.clear()


@router.callback_query()
async def log_callback_query(callback: CallbackQuery):
    logger.info(f"Callback data: {callback.data}")
