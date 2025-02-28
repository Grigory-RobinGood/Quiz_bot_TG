import logging

from aiogram import Router, F
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message
from aiogram_dialog import DialogManager, StartMode
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from db.db_functions import get_exchange_rates
from db.models import AsyncSessionLocal, Users, ExchangeRates
from keyboards.keyboards import main_kb, account_kb, get_balance_keyboard, exchange_kb, cancel_exchange_kb
from lexicon.lexicon_ru import LEXICON_RU
from services import filters as f, game
from services.FSM import DialogStates, ExchangeStates
from services.filters import StartGameCallbackData, BalanceCallbackData, ExchangeCallbackData, \
    ExchangeButtonCallbackData
from services.game import start_game
from services.user_dialog import rating_router

router = Router()
exchange_router = Router()
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


# Обработка кнопки Назад в меню Аккаунт
@router.callback_query(F.data == "back_to_account")
async def back_to_account(callback: CallbackQuery):
    await callback.message.delete()
    await process_account_command(callback)


# Обработка кнопки Обмен
@router.callback_query(ExchangeButtonCallbackData.filter())
async def show_exchange_rates(callback: CallbackQuery, session: AsyncSession):
    """Обработчик кнопки 'Обмен' — показывает актуальные курсы обмена."""
    exchange_text = await get_exchange_rates(session)
    await callback.message.edit_text(exchange_text, reply_markup=exchange_kb)


@exchange_router.callback_query(ExchangeCallbackData.filter())
async def ask_exchange_amount(callback: CallbackQuery, callback_data: ExchangeCallbackData, state: FSMContext):
    """Обработчик выбора направления обмена — запрашивает сумму"""
    await state.update_data(from_currency=callback_data.from_currency, to_currency=callback_data.to_currency)
    await callback.message.answer(
        f"🔄 Введите сумму для обмена {callback_data.from_currency} → {callback_data.to_currency}:"
    )
    await state.set_state(ExchangeStates.waiting_for_exchange_amount)


@exchange_router.callback_query(F.data == "cancel_exchange")
async def cancel_exchange(callback: CallbackQuery, state: FSMContext):
    """Отмена обмена"""
    await state.clear()
    await callback.message.delete()
    await callback.message.answer("❌ Обмен отменён.", reply_markup=exchange_kb)


@exchange_router.message(StateFilter(ExchangeStates.waiting_for_exchange_amount))
async def process_exchange(message: Message, state: FSMContext, session: AsyncSession):
    """Обрабатывает ввод суммы и выполняет обмен."""
    user_id = message.from_user.id
    user = await session.scalar(select(Users).where(Users.user_id == user_id))

    if not user:
        await message.answer("⚠️ Ошибка: пользователь не найден.", reply_markup=exchange_kb)
        return

    data = await state.get_data()
    from_currency = data["from_currency"]
    to_currency = data["to_currency"]

    try:
        amount = float(message.text)
        if amount <= 0:
            raise ValueError
    except ValueError:
        await message.answer("⚠️ Введите корректную сумму.")
        return

    # Проверяем баланс пользователя
    user_balance = getattr(user, f"balance_{from_currency.lower()}")
    if amount > user_balance:
        await message.answer("⚠️ Недостаточно средств для обмена.", reply_markup=exchange_kb)
        return

    # Получаем актуальный курс обмена
    rate = await session.scalar(select(ExchangeRates).filter_by(from_currency=from_currency, to_currency=to_currency))
    if not rate:
        await message.answer("⚠️ Ошибка: курс обмена не найден.", reply_markup=exchange_kb)
        return

    # Рассчитываем сумму после обмена
    exchanged_amount = amount * rate.rate

    # Обновляем баланс пользователя
    setattr(user, f"balance_{from_currency.lower()}", user_balance - amount)
    setattr(user, f"balance_{to_currency.lower()}", getattr(user, f"balance_{to_currency.lower()}") + exchanged_amount)

    await session.commit()

    await message.answer(text=f"✅ Обмен успешно завершён!\n"
                              f"{amount} {from_currency} → {exchanged_amount:.2f} {to_currency}",
                         reply_markup=exchange_kb)

    await state.clear()


@exchange_router.message()
async def debug_state(message: Message, state: FSMContext):
    current_state = await state.get_state()
    print(f"Текущее состояние: {current_state}")
