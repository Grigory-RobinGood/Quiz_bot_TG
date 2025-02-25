import logging

from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message
from aiogram_dialog import DialogManager, StartMode
from sqlalchemy import select

from db.models import AsyncSessionLocal, Users
from keyboards.keyboards import main_kb, account_kb, get_balance_keyboard
from lexicon.lexicon_ru import LEXICON_RU
from services import filters as f, game
from services.FSM import DialogStates
from services.filters import StartGameCallbackData, BalanceCallbackData
from services.game import start_game
from services.user_dialog import rating_router

router = Router()
logger = logging.getLogger(__name__)


# __________Этот хэндлер срабатывает на команду /account________________________________
@router.callback_query(f.AccountCallbackData.filter())
async def process_account_command(callback: CallbackQuery):
    try:
        # Редактируем предыдущее сообщение
        await callback.message.edit_text(
            text="Вы вошли в свой аккаунт",
            reply_markup=account_kb
        )
    except Exception as e:
        logger.error(f"Ошибка при редактировании сообщения: {e}")
        # Если редактирование не удалось, отправляем новое сообщение
        await callback.message.answer(text="Вы вошли в свой аккаунт", reply_markup=account_kb)


# Этот хэндлер срабатывает на команду /help
@router.callback_query(f.HelpCallbackData.filter())
async def process_help_command(callback: CallbackQuery):
    try:
        await callback.message.edit_text(
            text=LEXICON_RU['/help'],
            reply_markup=main_kb
        )
    except Exception as e:
        logger.error(f"Ошибка при редактировании сообщения: {e}")
        await callback.message.answer(text=LEXICON_RU['/help'], reply_markup=account_kb)


#______________________Хэндлеры для выбора лиги___________________________________
@router.callback_query(StartGameCallbackData.filter())
async def handle_start_game(call: CallbackQuery, callback_data: StartGameCallbackData, state: FSMContext):
    #Обработчик нажатия кнопки "Бронзовая лига".
    if callback_data.league == "Bronze":
        league = callback_data.league
        user_id = call.from_user.id

        async with AsyncSessionLocal() as session:
            try:
                # Отправляем сообщение о начале игры
                await call.message.edit_reply_markup()  # Убираем клавиатуру из сообщения
                await call.message.answer(f"Игра в {league} лиге начинается!")

                # Вызываем функцию старта игры
                await start_game(
                    session=session,
                    user_id=user_id,
                    league=league,
                    send_message=call.message.answer,
                    router=game.router,
                    state=state
                )

            except Exception as e:
                # Логируем ошибку и отправляем пользователю сообщение
                logger.error(f"Ошибка при запуске игры: {e}")
                await call.message.answer("Произошла ошибка при запуске игры. Попробуйте позже.")

    #Обработчик нажатия кнопки "Серебряная лига".

    if callback_data.league == "Silver":
        league = callback_data.league
        user_id = call.from_user.id

        async with AsyncSessionLocal() as session:
            try:
                # Отправляем сообщение о начале игры
                await call.message.edit_reply_markup()  # Убираем клавиатуру из сообщения
                await call.message.answer(f"Игра в {league} лиге начинается!")

                # Вызываем функцию старта игры
                await start_game(
                    session=session,
                    user_id=user_id,
                    league=league,
                    send_message=call.message.answer,
                    router=game.router,
                    state=state
                )

            except Exception as e:
                # Логируем ошибку и отправляем пользователю сообщение
                logger.error(f"Ошибка при запуске игры: {e}")
                await call.message.answer("Произошла ошибка при запуске игры. Попробуйте позже.")

    #Обработчик нажатия кнопки "Золотая лига".

    if callback_data.league == "Gold":
        league = callback_data.league
        user_id = call.from_user.id

        async with AsyncSessionLocal() as session:
            try:
                # Отправляем сообщение о начале игры
                await call.message.edit_reply_markup()  # Убираем клавиатуру из сообщения
                await call.message.answer(f"Игра в {league} лиге начинается!")

                # Вызываем функцию старта игры
                await start_game(
                    session=session,
                    user_id=user_id,
                    league=league,
                    send_message=call.message.answer,
                    router=game.router,
                    state=state
                )

            except Exception as e:
                # Логируем ошибку и отправляем пользователю сообщение
                logger.error(f"Ошибка при запуске игры: {e}")
                await call.message.answer("Произошла ошибка при запуске игры. Попробуйте позже.")


# Обработчик для запуска диалога рейтинга
@rating_router.callback_query(F.data == "user_rate")
async def start_rating_dialog(callback: CallbackQuery, dialog_manager: DialogManager):
    await callback.message.delete()
    await dialog_manager.start(state=DialogStates.rating, mode=StartMode.RESET_STACK)
    await callback.answer()


# Обработчик кнопки "Баланс"
@router.callback_query(BalanceCallbackData.filter())
async def show_balance(callback: CallbackQuery):
    user_id = callback.from_user.id

    async with AsyncSessionLocal() as session:
        result = await session.execute(select(Users).where(Users.user_id == user_id))
        user = result.scalars().first()

        if user:
            balance_text = (
                f"💰 *Ваш баланс:*\n"
                f"🥉 *Бронзовые монеты:* {user.balance_bronze}\n"
                f"🥈 *Серебряные монеты:* {user.balance_silver}\n"
                f"🥇 *Золотые монеты:* {user.balance_gold}\n"
                f"💵 *Рубли:* {user.balance_rubles:.2f}₽"
            )
        else:
            balance_text = "❌ Ошибка: Ваш профиль не найден в базе данных."

    await callback.message.edit_text(
        balance_text,
        parse_mode="Markdown",
        reply_markup=get_balance_keyboard()
    )


@router.callback_query(F.data == "back_to_account")
async def back_to_account(callback: CallbackQuery):
    await callback.message.delete()
    await process_account_command(callback)
