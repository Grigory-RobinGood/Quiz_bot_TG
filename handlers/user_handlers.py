import logging

from datetime import datetime

from aiogram import Router, F, Bot
from aiogram.enums import ContentType
from aiogram.exceptions import TelegramBadRequest
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message, InlineKeyboardMarkup, InlineKeyboardButton, PreCheckoutQuery
from aiogram_dialog import DialogManager, StartMode
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from db.db_functions import get_exchange_rates
from db.models import AsyncSessionLocal, Users, ExchangeRates, ProposedQuestion, SponsorChannel, user_subscriptions, \
    Transaction
from keyboards.keyboards import (main_kb, account_kb, get_balance_keyboard, exchange_kb, earn_coins_kb,
                                 add_or_cancel, top_up_keyboard)
from lexicon.lexicon_ru import LEXICON_RU
from services import filters as f, game
from services.FSM import DialogStates, ExchangeStates, ProposeQuestionState
from services.filters import StartGameCallbackData, BalanceCallbackData, ExchangeCallbackData, \
    ExchangeButtonCallbackData
from services.game import start_game
from services.services import process_telegram_pay, process_telegram_stars, get_yookassa_receipt
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


# ______________________Хэндлеры для выбора лиги___________________________________
@router.callback_query(StartGameCallbackData.filter())
async def handle_start_game(call: CallbackQuery, callback_data: StartGameCallbackData, state: FSMContext):
    # Обработчик нажатия кнопки "Бронзовая лига".
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

    # Обработчик нажатия кнопки "Серебряная лига".

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

    # Обработчик нажатия кнопки "Золотая лига".

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
                # f"🥉 *Бронзовые монеты:* {user.balance_bronze}\n"
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


# ------------------- Обработка кнопки "Пополнить" -------------------
@router.callback_query(F.data == "top_up_balance")
async def show_topup_options(callback: CallbackQuery):
    """ Показывает пользователю способы пополнения баланса """
    await callback.answer()  # Убираем "часики"
    await callback.message.edit_text("Выберите способ пополнения баланса:", reply_markup=top_up_keyboard)


# нажатие кнопки "Отмена"
@router.callback_query(F.data == "cancel")
async def cancel_topup(callback: CallbackQuery, state: FSMContext):
    """Обрабатывает нажатие кнопки 'Отмена' и возвращает в главное меню."""
    await state.clear()
    await callback.message.edit_text("Пополнение отменено.", reply_markup=get_balance_keyboard())


# выбор способа пополнения и ввод суммы платежа
@router.callback_query(lambda c: c.data in ["topup_card", "topup_stars"])
async def handle_payment_method(callback: CallbackQuery, state: FSMContext):
    """Обработка выбора метода оплаты"""
    payment_method = callback.data
    await state.update_data(payment_method=payment_method)

    await callback.message.edit_text("Введите сумму пополнения (в рублях):")
    await state.set_state("waiting_for_amount")


# создание платежа
@router.message(F.text, StateFilter("waiting_for_amount"))
async def create_payment(message: Message, state: FSMContext):
    """ Получает сумму и создаёт платёж в Telegram Pay или Telegram Stars """
    data = await state.get_data()
    payment_method = data.get("payment_method")

    try:
        amount = float(message.text)
        if amount < 10:
            await message.answer("❌ Сумма должна быть больше 10 руб. Введите корректное значение.")
            return
    except ValueError:
        await message.answer("❌ Некорректное значение. Введите сумму целым числом.")
        return

    await state.update_data(original_amount=amount)  #  Сохраняем сумму в рублях

    if payment_method == "topup_card":
        await process_telegram_pay(message, amount)
    elif payment_method == "topup_stars":
        await process_telegram_stars(message, amount)


@router.pre_checkout_query(lambda query: True)
async def pre_checkout_query_handler(pre_checkout_query: PreCheckoutQuery):
    """Обработчик проверки платежа Telegram Pay перед подтверждением."""
    await pre_checkout_query.answer(ok=True)


# обработка успешной оплаты
async def successful_payment_handler(message: Message, session: AsyncSession, state: FSMContext):
    """ Обработчик успешного платежа через Telegram Pay и запрос чека из ЮКассы. """
    payment_info = message.successful_payment
    user_id = message.from_user.id
    #invoice_payload = payment_info.invoice_payload  # Уникальный ID платежа

    # Получаем сохранённые данные о платеже
    data = await state.get_data()
    payment_method = data.get("payment_method", "topup_card")  # По умолчанию "карта"

    # Определяем сумму пополнения
    if payment_method == "topup_stars":
        amount = payment_info.total_amount * 100  # Telegram Stars передаёт сумму без копеек
    else:
        amount = payment_info.total_amount / 100  # Для карт Telegram Pay передаёт сумму в копейках

    # Обновляем баланс пользователя
    result = await session.execute(select(Users).filter_by(user_id=user_id))
    user = result.scalars().first()

    if user:
        user.balance_rubles += amount
        session.add(user)
        await session.commit()

        # Записываем транзакцию
        transaction = Transaction(
            user_id=user_id,
            amount=amount,
            currency="RUB",
            transaction_type="Пополнение"
        )
        session.add(transaction)
        await session.commit()

        # Запрос чека из ЮКассы (только если оплата картой)
        if payment_method == "topup_card":
            receipt_data = await get_yookassa_receipt(payment_info.provider_payment_charge_id)

            if "receipt_registration" in receipt_data and receipt_data["receipt_registration"] == "succeeded":
                receipt_url = receipt_data.get("receipt", {}).get("url", "Чек недоступен")
                receipt_text = f"✅ Оплата на {amount:.2f} RUB успешно проведена!\n" \
                               f"🧾 [📄 Посмотреть чек]({receipt_url})"
            else:
                receipt_text = f"✅ Оплата на {amount:.2f} RUB успешно проведена!\n" \
                               "⚠ Чек пока не зарегистрирован. Попробуйте позже."
        else:
            receipt_text = f"✅ Оплата на {amount:.2f} RUB успешно проведена!"

        await message.answer(receipt_text, parse_mode="Markdown", reply_markup=get_balance_keyboard())

    else:
        await message.answer("❌ Ошибка: ваш аккаунт не найден. Свяжитесь с поддержкой.")

    await state.clear()  # Очищаем состояние после успешного платежа


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
        await message.answer("⚠️ Введите корректную сумму.\n Например, 0.6 (разделитель 'точка')")
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


@router.callback_query(F.data == "earn_coins")
async def earn_coins_menu(callback: CallbackQuery):
    """Обработчик кнопки 'Заработать монеты' — показывает клавиатуру с вариантами"""
    await callback.message.edit_text("💰 Выберите способ заработка монет:", reply_markup=earn_coins_kb)


@router.callback_query(F.data == "back_to_account")
async def back_to_main_menu(callback: CallbackQuery):
    """Обработчик кнопки 'Назад' — возвращает в главное меню"""
    await callback.message.edit_text("Вы вошли в свой аккаунт", reply_markup=account_kb)


# _____________Обработка предложения вопроса пользователем____________________
@router.callback_query(F.data == "propose_question")
async def propose_question(callback: CallbackQuery, state: FSMContext):
    """Запуск процесса предложения вопроса"""
    await callback.message.answer("✍ Введите текст вашего вопроса:")
    await state.set_state(ProposeQuestionState.waiting_for_question_text)


@router.message(ProposeQuestionState.waiting_for_question_text)
async def propose_question_text(message: Message, state: FSMContext):
    await state.update_data(question_text=message.text)
    await message.answer("✅ Введите правильный ответ:")
    await state.set_state(ProposeQuestionState.waiting_for_correct_answer)


@router.message(ProposeQuestionState.waiting_for_correct_answer)
async def propose_correct_answer(message: Message, state: FSMContext):
    await state.update_data(correct_answer=message.text)
    await message.answer("❌ Введите первый неправильный ответ:")
    await state.set_state(ProposeQuestionState.waiting_for_wrong_answer_1)


@router.message(ProposeQuestionState.waiting_for_wrong_answer_1)
async def propose_wrong_answer_1(message: Message, state: FSMContext):
    await state.update_data(answer_2=message.text)
    await message.answer("❌ Введите второй неправильный ответ:")
    await state.set_state(ProposeQuestionState.waiting_for_wrong_answer_2)


@router.message(ProposeQuestionState.waiting_for_wrong_answer_2)
async def propose_wrong_answer_2(message: Message, state: FSMContext):
    await state.update_data(answer_3=message.text)
    await message.answer("❌ Введите третий неправильный ответ:")
    await state.set_state(ProposeQuestionState.waiting_for_wrong_answer_3)


@router.message(ProposeQuestionState.waiting_for_wrong_answer_3)
async def propose_wrong_answer_3(message: Message, state: FSMContext):
    await state.update_data(answer_4=message.text)

    data = await state.get_data()
    question_preview = (f"🔎 Проверьте ваш вопрос:\n\n"
                        f"❓ Вопрос: {data['question_text']}\n"
                        f"✅ Правильный ответ: {data['correct_answer']}\n"
                        f"❌ Неправильные ответы:\n"
                        f"1️⃣ {data['answer_2']}\n"
                        f"2️⃣ {data['answer_3']}\n"
                        f"3️⃣ {data['answer_4']}")

    await message.answer(question_preview, reply_markup=add_or_cancel)
    await state.set_state(ProposeQuestionState.check_and_add_question)


@router.callback_query(ProposeQuestionState.check_and_add_question)
async def check_and_add_proposed_question(callback: CallbackQuery, state: FSMContext, session: AsyncSession):
    if callback.data == "cancel":
        await callback.message.answer("❌ Добавление вопроса отменено.", reply_markup=earn_coins_kb)
        await state.clear()
        return

    data = await state.get_data()
    user_id = callback.from_user.id

    new_question = ProposedQuestion(
        question_text=data["question_text"],
        correct_answer=data["correct_answer"],
        answer_2=data["answer_2"],
        answer_3=data["answer_3"],
        answer_4=data["answer_4"],
        created_by_user_id=user_id,
        created_at=datetime.utcnow()
    )
    logger.info(f"Adding question: {new_question}")
    session.add(new_question)
    await session.commit()

    await callback.message.answer("✅ Ваш вопрос отправлен на модерацию! Спасибо за участие.",
                                  reply_markup=earn_coins_kb)
    await state.clear()


# ________________________ Подписка на спонсорские каналы_________________________________
@router.callback_query(lambda c: c.data == "subscribe_sponsors")
async def show_sponsor_channels(callback: CallbackQuery, session: AsyncSession):
    user_id = callback.from_user.id

    # Получаем список всех спонсорских каналов
    result = await session.execute(select(SponsorChannel))
    sponsor_channels = result.scalars().all()

    if not sponsor_channels:
        await callback.answer("Сейчас нет доступных спонсорских каналов.", show_alert=True)
        return

    # Получаем список каналов, на которые подписан пользователь
    sub_result = await session.execute(select(user_subscriptions.c.channel_id)
                                       .where(user_subscriptions.c.user_id == user_id))
    subscribed_channels = {row[0] for row in sub_result.fetchall()}

    # Формируем клавиатуру с кнопками (отмечаем подписанные каналы)
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(
                text=f"{'✅' if channel.id in subscribed_channels else '❌'} {channel.name}",
                url=channel.link if channel.link.startswith("http") else f"https://t.me/{channel.link.lstrip('@')}"
            )
        ]
        for channel in sponsor_channels
    ])

    # Добавляем кнопку проверки подписки и кнопку назад
    keyboard.inline_keyboard.append([InlineKeyboardButton(text="🔄 Проверить подписку",
                                                          callback_data="check_subscription")])
    keyboard.inline_keyboard.append([InlineKeyboardButton(text="🔙 Назад",
                                                          callback_data="menu")])

    await callback.message.edit_text(
        "Подпишитесь на каналы спонсоров, затем нажмите '🔄 Проверить подписку':",
        reply_markup=keyboard
    )


@router.callback_query(lambda c: c.data == "check_subscription")
async def check_subscription(callback: CallbackQuery, session: AsyncSession, bot: Bot):
    user_id = callback.from_user.id

    # Загружаем все спонсорские каналы из БД
    result = await session.execute(select(SponsorChannel))
    sponsor_channels = result.scalars().all()

    if not sponsor_channels:
        await callback.answer("Нет доступных спонсорских каналов.", show_alert=True)
        return

    new_subscriptions = []  # Список новых подписок

    for channel in sponsor_channels:
        chat_id = channel.link.replace("https://t.me/", "").replace("/", "")

        try:
            chat_member = await bot.get_chat_member(chat_id, user_id)

            if chat_member.status in ["member", "administrator", "creator"]:
                # Проверяем, есть ли уже запись в user_subscriptions
                existing_subscription = await session.execute(
                    select(user_subscriptions)
                    .where(user_subscriptions.c.user_id == user_id,
                           user_subscriptions.c.channel_id == channel.id)
                )
                if not existing_subscription.first():
                    new_subscriptions.append(channel.id)

        except TelegramBadRequest:
            continue  # Ошибка запроса — канал недоступен или бот не админ

    if new_subscriptions:
        # Записываем новые подписки в user_subscriptions
        for channel_id in new_subscriptions:
            await session.execute(user_subscriptions.insert().values(user_id=user_id, channel_id=channel_id))

        # Начисляем 100 серебряных монет за каждую подписку
        user = await session.execute(select(Users).where(Users.user_id == user_id))
        user = user.scalars().first()
        if user:
            user.balance_silver += 100 * len(new_subscriptions)

        await session.commit()
        await callback.answer(f"Вы подписались на {len(new_subscriptions)} канал(а), начислено "
                              f"{100 * len(new_subscriptions)} серебряных монет!", show_alert=True)

    else:
        await callback.answer("Вы уже подписаны на все каналы.", show_alert=True)

    # Получаем актуальный список подписок после проверки
    sub_result = await session.execute(select(user_subscriptions.c.channel_id)
                                       .where(user_subscriptions.c.user_id == user_id))
    subscribed_channels = {row[0] for row in sub_result.fetchall()}

    # Формируем новую клавиатуру с актуальными статусами подписок
    new_keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(
                text=f"{'✅' if channel.id in subscribed_channels else '❌'} {channel.name}",
                url=channel.link if channel.link.startswith("http") else f"https://t.me/{channel.link.lstrip('@')}"
            )
        ]
        for channel in sponsor_channels
    ])
    new_keyboard.inline_keyboard.append([InlineKeyboardButton(text="🔄 Проверить подписку",
                                                              callback_data="check_subscription")])
    new_keyboard.inline_keyboard.append([InlineKeyboardButton(text="🔙 Назад",
                                                              callback_data="earn_coins")])

    # Проверяем, изменилось ли что-то
    old_text = callback.message.text
    new_text = "Подпишитесь на каналы спонсоров, затем нажмите '🔄 Проверить подписку':"
    old_keyboard = callback.message.reply_markup

    if old_text != new_text or old_keyboard != new_keyboard:
        await callback.message.edit_text(new_text, reply_markup=new_keyboard)


# ______________________ Приглашения друзей в бота________________________________
@router.callback_query(lambda c: c.data == "invite_friend")
async def invite_friend(callback: CallbackQuery):
    user_id = callback.from_user.id
    bot_username = (await callback.bot.me()).username  # Получаем username бота

    referral_link = f"https://t.me/{bot_username}?start={user_id}"

    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔗 Поделиться ссылкой",
                              switch_inline_query=f"Присоединяйся к игре! {referral_link}")],
        [InlineKeyboardButton(text="🔙 Назад",
                              callback_data="earn_coins")]
    ])

    await callback.message.edit_text(
        f"👥 Приглашайте друзей и получайте монеты!\n\n"
        f"💰 Вы получите 500 серебряных монет за каждого приглашенного друга.\n"
        f"🔗 Ваша реферальная ссылка:\n\n<code>{referral_link}</code>",
        reply_markup=keyboard
    )
