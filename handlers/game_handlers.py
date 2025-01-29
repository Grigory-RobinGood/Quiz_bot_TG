import asyncio
import logging
import random

from typing import Optional
from aiogram import Router, types, F
from aiogram.fsm.context import FSMContext
from aiogram.filters import StateFilter
from aiogram.types import CallbackQuery

from middleware.game_mdwr import CallbackQueryMiddleware
from services.FSM import ProcessGameState
from keyboards.keyboards import create_question_keyboard
from db.db_functions import get_question

from services.filters import StartGameCallbackData, CallbackQueryFilter

logger = logging.getLogger(__name__)
router = Router()
# Инициализация middleware
callback_query_middleware = CallbackQueryMiddleware()
router.callback_query.middleware(callback_query_middleware)


@router.callback_query()
async def log_callback_query(callback: CallbackQuery):
    logger.info(f"Callback data: {callback.data}")


@router.callback_query(StartGameCallbackData.filter())
async def start_game(callback: CallbackQuery, callback_data: StartGameCallbackData, state: FSMContext):
    league = callback_data.league

    # Получаем вопросы для выбранной лиги
    questions = await get_question(league)  # Ожидается список словарей
    if not questions:
        await callback.message.answer(f"Недостаточно вопросов для {league} лиги!")
        return

    # Перемешиваем порядок вопросов
    random.shuffle(questions)

    # Инициализация игрового состояния
    await state.update_data(
        league=league,
        questions=questions,
        current_score=0,
        hints_used={
            "remove_two": False,
            "take_money": False,
            "insure": False
        }
    )
    await callback.message.answer(f"Вы выбрали {league} лигу. Начинаем игру!")
    await send_next_question(callback.message, state)


async def send_next_question(message: types.Message, state: FSMContext):
    data = await state.get_data()
    questions = data["questions"]

    # Проверяем, остались ли вопросы
    if not questions:
        current_score = data["current_score"]
        await message.answer(f"Игра завершена! Ваш итоговый счёт: {current_score}.")
        await state.clear()
        return

    # Берём следующий вопрос
    current_question = questions.pop(0)
    correct_answer = current_question["correct_answer"]
    incorrect_answers = current_question["incorrect_answers"]
    answers = [correct_answer] + incorrect_answers  # Исправлено: объединяем ответы

    # Сохраняем данные в состоянии
    await state.update_data(questions=questions, current_question=current_question, answers=answers)

    # Создаём клавиатуру с вариантами ответов
    keyboard = create_question_keyboard(
        question_id=current_question["id"],
        answers=answers,
        hints={
            "hint_insure": "Застраховать сумму",
            "hint_remove_two": "Убрать два ответа",
            "hint_take_money": "Забрать деньги"
        }
    )

    # Отправляем вопрос пользователю
    await message.answer(
        f"Вопрос: {current_question['text']}\n\n"
        f"A) {answers[0]}\n"
        f"B) {answers[1]}\n"
        f"C) {answers[2]}\n"
        f"D) {answers[3]}",
        reply_markup=keyboard
    )
    await state.set_state(ProcessGameState.waiting_for_answer)


@router.callback_query(F.data.startswith("answer:"), StateFilter(ProcessGameState.waiting_for_answer))
async def process_answer(callback: CallbackQuery, state: FSMContext):
    logger.info(f"Callback data: {callback.data}")  # Логируем данные callback_query

    data = await state.get_data()
    current_question = data["current_question"]
    correct_answer = current_question["correct_answer"]
    answers = data["answers"]

    try:
        answer_index = int(callback.data.split(":")[1])
        selected_answer = answers[answer_index]

        if selected_answer == correct_answer:
            current_score = data["current_score"] + current_question["score"]
            await state.update_data(current_score=current_score)
            await callback.message.answer("Правильно!")
            await send_next_question(callback.message, state)  # Вызываем следующий вопрос
        else:
            hints_used = data["hints_used"]
            if hints_used.get("insure"):
                guaranteed_score = data["current_score"]
                await callback.message.answer(
                    f"Вы проиграли, но застрахованная сумма: {guaranteed_score}!"
                )
            else:
                await callback.message.answer("Вы проиграли. Ваш выигрыш: 0.")
            await state.clear()
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
