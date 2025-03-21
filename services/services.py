import base64
import uuid

import aiohttp
from aiogram.types import Message, LabeledPrice
from aiogram_dialog import DialogManager
from datetime import datetime, timedelta
import pytz
from sqlalchemy import func, select, and_
from aiocache import cached

from config_data.config import PAY_TOKEN, SHOP_ID, SECRET_KEY
from db.models import (
    Users, Game, ProposedQuestion, async_session_maker,
    user_referrals, user_subscriptions, LeagueEnum
)


# Функция для получения временного диапазона недели
def get_current_week_range():
    tz = pytz.timezone('Europe/Moscow')
    now = datetime.now(tz)

    # Находим начало недели (понедельник 00:00)
    start = (now - timedelta(days=now.weekday())).replace(hour=0, minute=0, second=0, microsecond=0)
    # Находим конец недели (воскресенье 23:59)
    end = start + timedelta(days=6, hours=23, minutes=59)

    return start.astimezone(pytz.utc), end.astimezone(pytz.utc)


# Кеширование рейтинга на 5 минут
@cached(ttl=300)
async def get_cached_rating_data():
    start_week, end_week = get_current_week_range()

    async with async_session_maker() as session:
        # Рейтинг по лигам (бронза, серебро, золото)
        league_ratings = {}
        for league in LeagueEnum:
            ratings = await session.execute(
                select(
                    Game.user_id,
                    func.sum(Game.score).label('total_score')
                )
                .where(and_(
                    Game.league == league,
                    Game.created_at.between(start_week, end_week)
                ))
                .group_by(Game.user_id)
                .order_by(func.sum(Game.score).desc())
            )
            league_ratings[league] = ratings.all()

        # Рейтинг по предложенным вопросам
        question_ratings = await session.execute(
            select(
                ProposedQuestion.created_by_user_id,
                func.count(ProposedQuestion.id).label('total_questions')
            )
            .where(and_(
                ProposedQuestion.created_at.between(start_week, end_week)
            ))
            .group_by(ProposedQuestion.created_by_user_id)
            .order_by(func.count(ProposedQuestion.id).desc())
        )
        question_ratings = question_ratings.all()

        # Рейтинг по подпискам на каналы спонсоров
        subscription_ratings = await session.execute(
            select(
                Users.user_id,
                func.count(user_subscriptions.c.user_id).label('total_subscriptions')
            )
            .join(user_subscriptions, user_subscriptions.c.user_id == Users.user_id)
            .where(and_(
                Users.created_at.between(start_week, end_week)
            ))
            .group_by(Users.user_id)
            .order_by(func.count(user_subscriptions.c.user_id).desc())
        )
        subscription_ratings = subscription_ratings.all()

        # Рейтинг по приглашенным друзьям
        referral_ratings = await session.execute(
            select(
                user_referrals.c.referrer_id,
                func.count(user_referrals.c.referred_id).label('total_referrals')
            )
            .group_by(user_referrals.c.referrer_id)
            .order_by(func.count(user_referrals.c.referred_id).desc())
        )
        referral_ratings = referral_ratings.all()

    return {
        "league_ratings": league_ratings,
        "question_ratings": question_ratings,
        "subscription_ratings": subscription_ratings,
        "referral_ratings": referral_ratings,
    }


# Функция для получения данных о рейтинге
async def get_rating_data(dialog_manager: DialogManager, **kwargs):
    user = dialog_manager.event.from_user
    cached_data = await get_cached_rating_data()

    league_ratings = cached_data["league_ratings"]
    question_ratings = cached_data["question_ratings"]
    subscription_ratings = cached_data["subscription_ratings"]
    referral_ratings = cached_data["referral_ratings"]

    # Находим место пользователя в каждом рейтинге
    user_league_ranks = {}
    for league, ratings in league_ratings.items():
        user_league_ranks[league] = next((i for i, (uid, _) in enumerate(ratings, 1) if uid == user.id), None)

    user_question_rank = next((i for i, (uid, _) in enumerate(question_ratings, 1) if uid == user.id), None)
    user_subscription_rank = next((i for i, (uid, _) in enumerate(subscription_ratings, 1) if uid == user.id), None)
    user_referral_rank = next((i for i, (uid, _) in enumerate(referral_ratings, 1) if uid == user.id), None)

    # Получаем данные для пагинации (5 строк до и 5 строк после пользователя)
    def get_paginated_ratings(ratings, user_rank):
        if user_rank is None:
            return []
        start_index = max(0, user_rank - 6)
        end_index = min(len(ratings), user_rank + 5)
        return ratings[start_index:end_index]

    # Форматируем данные для отображения
    def format_rating(ratings, user_id, label, is_league=False):
        result = []
        for rank, (uid, value) in enumerate(ratings, start=1):
            if uid == user_id:
                result.append(f"🏅 {rank}. Вы: {value} {label}")
            else:
                if rank == 1:
                    result.append(f"🥇 {rank}. Пользователь {uid}: {value} {label}")
                elif rank == 2:
                    result.append(f"🥈 {rank}. Пользователь {uid}: {value} {label}")
                elif rank == 3:
                    result.append(f"🥉 {rank}. Пользователь {uid}: {value} {label}")
                else:
                    result.append(f"📊 {rank}. Пользователь {uid}: {value} {label}")
        return "\n".join(result)

    # Формируем текст для каждой лиги
    league_rating_texts = []
    for league, ratings in league_ratings.items():
        user_rank = user_league_ranks[league]
        paginated_ratings = get_paginated_ratings(ratings, user_rank)
        league_rating_texts.append(
            f"📊 Рейтинг в лиге {league.value}:\n"
            f"{format_rating(paginated_ratings, user.id, 'баллов')}"
        )

    question_rating_text = format_rating(
        get_paginated_ratings(question_ratings, user_question_rank),
        user.id, "вопросов"
    )
    subscription_rating_text = format_rating(
        get_paginated_ratings(subscription_ratings, user_subscription_rank),
        user.id, "подписок"
    )
    referral_rating_text = format_rating(
        get_paginated_ratings(referral_ratings, user_referral_rank),
        user.id, "друзей"
    )

    return {
        "league_ratings": "\n\n".join(league_rating_texts),
        "question_rating": question_rating_text,
        "subscription_rating": subscription_rating_text,
        "referral_rating": referral_rating_text,
    }


# Функции для платежей
async def check_payment_status(payment_id: str) -> bool:
    """Проверяет статус платежа в ЮКассе."""
    auth_string = f"{SHOP_ID}:{SECRET_KEY}"
    encoded_auth = base64.b64encode(auth_string.encode()).decode()

    headers = {"Authorization": f"Basic {encoded_auth}"}

    async with aiohttp.ClientSession() as session:
        async with session.get(f"https://api.yookassa.ru/v3/payments/{payment_id}", headers=headers) as resp:
            response_data = await resp.json()

    return response_data.get("status") == "succeeded"


# async def process_yookassa_payment(message: Message, state: FSMContext, amount: float, payment_method: str):
#     """Создаёт платёж в ЮКассе."""
#     payment_id = str(uuid.uuid4())
#
#     payment_data = {
#         "amount": {"value": f"{amount:.2f}", "currency": "RUB"},
#         "capture": True,
#         "confirmation": {"type": "redirect", "return_url": "https://t.me/YOUR_BOT"},
#         "description": f"Пополнение баланса на {amount} RUB",
#         "metadata": {"user_id": message.from_user.id, "payment_method": payment_method}
#     }
#
#     auth_string = f"{SHOP_ID}:{SECRET_KEY}"
#     encoded_auth = base64.b64encode(auth_string.encode()).decode()
#
#     headers = {
#         "Authorization": f"Basic {encoded_auth}",
#         "Content-Type": "application/json",
#         "Idempotence-Key": payment_id
#     }
#
#     async with aiohttp.ClientSession() as session:
#         async with session.post("https://api.yookassa.ru/v3/payments", json=payment_data, headers=headers) as resp:
#             response_data = await resp.json()
#             print(response_data)  # Логируем ответ для отладки
#
#     if "confirmation" in response_data:
#         payment_url = response_data["confirmation"]["confirmation_url"]
#         await message.answer(f"💳 Перейдите по ссылке для оплаты: [Оплатить]({payment_url})", parse_mode="Markdown")
#         await state.update_data(payment_id=payment_id, amount=amount)
#         await state.set_state("waiting_for_payment")
#     else:
#         error_message = response_data.get("description", "Ошибка при создании платежа.")
#         await message.answer(f"❌ Ошибка: {error_message}")


async def process_telegram_pay(message: Message, amount: float):
    """Создаёт платёж через Telegram Pay."""
    prices = [LabeledPrice(label="Пополнение баланса", amount=int(amount * 100))]  # В копейках

    await message.bot.send_invoice(
        chat_id=message.chat.id,
        title="Пополнение баланса",
        description=f"Пополнение на {amount} RUB",
        payload=str(uuid.uuid4()),
        provider_token=PAY_TOKEN,
        currency="RUB",
        prices=prices,
        start_parameter="top_up"
    )


async def process_telegram_stars(message: Message, amount: float):
    """Создаёт платёж через Telegram Stars с конвертацией."""
    stars_amount = amount // 1.67  # Курс звезд к РУБ
    await message.answer(f"🔹 Для пополнения {amount:.2f} RUB вам нужно отправить {stars_amount:.0f} Telegram Stars.")

    # Отправляем запрос на перевод звёзд (примерный код, уточните детали у Telegram API)
    await message.bot.send_invoice(
        chat_id=message.chat.id,
        title="Оплата Telegram Stars",
        description=f"Пополнение баланса на {amount:.2f} RUB",
        payload=str(uuid.uuid4()),
        provider_token="STARS_PROVIDER_TOKEN",  # Замените на ваш токен
        currency="XTR",  # Telegram Stars
        prices=[LabeledPrice(label="Пополнение баланса", amount=int(stars_amount))],
        start_parameter="top_up_stars"
    )
