import logging

from aiogram import Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery

from db.models import AsyncSessionLocal
from keyboards.keyboards import main_kb, account_kb
from lexicon.lexicon_ru import LEXICON_RU
from services import filters as f, game
from services.filters import StartGameCallbackData
from services.game import start_game

router = Router()
logger = logging.getLogger(__name__)


# Этот хэндлер срабатыввает на команду /account
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
async def handle_bronze_league_start(call: CallbackQuery,
                                     callback_data: StartGameCallbackData,
                                     state: FSMContext):

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


# @router.callback_query()
# async def debug_callback(call: CallbackQuery):
#     print(f"Получен callback: {call.data}")  # Выведет любые колбэки
#     await call.answer("Колбэк получен!", show_alert=True)
