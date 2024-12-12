from aiogram.types import CallbackQuery
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.sql.expression import func
from db.models import Users, Game, Question
import random
import logging
import asyncio

logger = logging.getLogger(__name__)

# Настройки времени для каждой лиги
LEAGUE_SETTINGS = {
    "Bronze": {"cost": 0, "time_limit": 60},
    "Silver": {"cost": 1000, "currency": "silver", "time_limit": 50},
    "Gold": {"cost": 500, "currency": "gold", "time_limit": 40},
}

# Баллы за каждый вопрос
SCORE_TABLE = [
    5, 10, 20, 50, 100, 200, 300, 400, 500, 1000,
    2000, 3000, 4000, 5000, 10000
]


async def get_user_answer(callback_query: CallbackQuery) -> str:
    """
    Функция для получения ответа пользователя в Telegram.

    Аргументы:
    - callback_query: CallbackQuery — объект обратного вызова Telegram.

    Возвращает:
    - str: выбранный пользователем ответ (A, B, C, D).
    """
    return callback_query.data  # Данные, содержащие ответ пользователя.


async def start_game(session: Session, user_id: int, league: str, send_message):
    """
    Запуск игры для пользователя.

    Args:
        session (Session): Сессия SQLAlchemy для работы с базой данных.
        user_id (int): ID пользователя.
        league (str): Лига игры ('Bronze', 'Silver', 'Gold').
        send_message (callable): Функция для отправки сообщений пользователю.

    Returns:
        None
    """
    try:
        # Проверяем, существует ли пользователь
        user = session.query(Users).filter(Users.id == user_id).first()
        if not user:
            await send_message("Пользователь не найден.")
            return

        # Проверяем баланс пользователя для выбранной лиги
        league_config = LEAGUE_SETTINGS.get(league)
        if not league_config:
            await send_message("Неверная лига.")
            return

        if league != "Bronze":
            if league_config["currency"] == "silver" and user.balance_silver < league_config["cost"]:
                await send_message("Недостаточно серебряных монет для начала игры.")
                return
            elif league_config["currency"] == "gold" and user.balance_gold < league_config["cost"]:
                await send_message("Недостаточно золотых монет для начала игры.")
                return

        # Списываем стоимость игры
        if league != "Bronze":
            if league_config["currency"] == "silver":
                user.balance_silver -= league_config["cost"]
            elif league_config["currency"] == "gold":
                user.balance_gold -= league_config["cost"]
            session.commit()

        # Создаем запись об игре
        new_game = Game(user_id=user_id, league=league, score=0)
        session.add(new_game)
        session.commit()

        # Генерируем список вопросов (по 5 для каждого уровня сложности)
        questions = []
        for difficulty in ["Easy", "Medium", "Hard"]:
            questions += (
                session.query(Question)
                .filter(Question.league == league, Question.difficulty == difficulty)
                .order_by(func.random())
                .limit(5)
                .all()
            )

        if len(questions) < 15:
            await send_message("Недостаточно вопросов для игры в выбранной лиге.")
            return

        # Переменные для подсказок и игры
        current_score = 0
        guaranteed_score = 0
        hints_used = {"remove_two": False, "take_money": False}

        for idx, question in enumerate(questions, 1):
            # Перемешиваем ответы
            answers = [
                question.correct_answer,
                question.answer_2,
                question.answer_3,
                question.answer_4
            ]
            random.shuffle(answers)

            # Отправляем вопрос пользователю
            await send_message(
                f"Вопрос {idx}: {question.question_text}\n"
                f"1) {answers[0]}\n"
                f"2) {answers[1]}\n"
                f"3) {answers[2]}\n"
                f"4) {answers[3]}"
            )

            # Устанавливаем таймер
            try:
                user_answer = await asyncio.wait_for(
                    get_user_answer(), timeout=league_config["time_limit"]
                )
            except asyncio.TimeoutError:
                await send_message("Время вышло! Игра завершена.")
                break

            # Обрабатываем подсказки
            if user_answer == "hint_insure":
                guaranteed_score = current_score
                await send_message(f"Вы застраховали сумму: {guaranteed_score} баллов.")
                continue

            elif user_answer == "hint_remove_two" and not hints_used["remove_two"]:
                hints_used["remove_two"] = True
                wrong_answers = [ans for ans in answers if ans != question.correct_answer]
                random.shuffle(wrong_answers)
                updated_answers = [
                    question.correct_answer,
                    wrong_answers[0]
                ]
                random.shuffle(updated_answers)
                await send_message(
                    f"Подсказка! Выберите правильный ответ:\n"
                    f"1) {updated_answers[0]}\n"
                    f"2) {updated_answers[1]}"
                )
                continue

            elif user_answer == "hint_take_money":
                user.balance_silver += current_score
                session.commit()
                await send_message(
                    f"Вы забрали сумму: {current_score} баллов. Игра завершена."
                )
                break

            # Проверяем ответ
            if answers[int(user_answer) - 1] == question.correct_answer:
                current_score += SCORE_TABLE[idx - 1]
                await send_message(f"Правильно! Ваши баллы: {current_score}")
            else:
                await send_message(f"Неправильно. Правильный ответ: {question.correct_answer}")
                break

        # Итог игры
        new_game.score = current_score
        user.balance_silver += guaranteed_score
        session.commit()

        await send_message(f"Игра завершена. Ваши баллы: {current_score}")

    except SQLAlchemyError as e:
        session.rollback()
        logger.error(f"Ошибка базы данных: {e}")
        await send_message("Ошибка базы данных.")

    except Exception as e:
        logger.error(f"Неожиданная ошибка: {e}")
        await send_message("Произошла ошибка.")

    finally:
        session.close()
