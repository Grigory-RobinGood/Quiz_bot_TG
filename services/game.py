import random
import logging
import asyncio

from aiogram import Router
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from sqlalchemy.sql.expression import func
from sqlalchemy.future import select
from sqlalchemy.exc import SQLAlchemyError

from db.models import Users, Game, Question
from handlers.game_handlers import wait_for_callback_query

logger = logging.getLogger(__name__)

router = Router()

# Настройки времени для каждой лиги
LEAGUE_SETTINGS = {
    "Bronze": {"cost": 0, "currency": None, "time_limit": 60},
    "Silver": {"cost": 1000, "currency": "silver", "time_limit": 50},
    "Gold": {"cost": 500, "currency": "gold", "time_limit": 40},
}

# Баллы за каждый вопрос
SCORE_TABLE = [
    5, 10, 20, 50, 100, 200, 300, 400, 500, 1000,
    2000, 3000, 4000, 5000, 10000
]


async def start_game(session, user_id: int, league: str, send_message, router):
    """
    Запуск игры для пользователя.

    Args:
        session: Асинхронная сессия SQLAlchemy.
        user_id (int): ID пользователя.
        league (str): Лига игры ('Bronze', 'Silver', 'Gold').
        send_message (callable): Функция для отправки сообщений пользователю.
        router (Router): Router для обработки временных callback-хендлеров.

    Returns:
        None
    """
    try:
        # Проверяем, существует ли пользователь
        result = await session.execute(select(Users).where(Users.user_id == user_id))
        user = result.scalars().first()

        if not user:
            await send_message("Пользователь не найден. Зарегистрируйтесь для начала игры.")
            return

        # Проверяем настройки лиги
        league_config = LEAGUE_SETTINGS.get(league)
        if not league_config:
            await send_message("Неверная лига.")
            return

        # Проверяем баланс пользователя
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
            await session.commit()

        # Генерируем список вопросов
        questions = []
        for difficulty in ["Easy", "Medium", "Hard"]:
            result = await session.execute(
                select(Question)
                .where(Question.league == league, Question.difficulty == difficulty)
            )
            num_questions = len(result.scalars().all())

            if num_questions < 5:
                await send_message(
                    f"Недостаточно вопросов уровня {difficulty} в лиге {league}. "
                    f"Найдено {num_questions}, необходимо 5."
                )
                return

            result = await session.execute(
                select(Question)
                .where(Question.league == league, Question.difficulty == difficulty)
                .order_by(func.random())
                .limit(5)
            )
            questions += result.scalars().all()

        if len(questions) < len(SCORE_TABLE):
            await send_message("В базе недостаточно вопросов для игры.")
            return

        # Создаём новую игру
        new_game = Game(user_id=user_id, league=league, score=0)
        session.add(new_game)
        await session.commit()

        # Начинаем игру
        current_score = 0
        guaranteed_score = 0
        hints_used = {"remove_two": False, "take_money": False, "insure": False}

        for idx, question in enumerate(questions, 1):
            answers = [
                question.correct_answer,
                question.answer_2,
                question.answer_3,
                question.answer_4
            ]
            random.shuffle(answers)
            hints = {
                "hint_insure": "Застраховать сумму",
                "hint_remove_two": "Убрать два ответа",
                "hint_take_money": "Забрать деньги"
            }

            # Создаем кнопки с буквами и подсказками
            answer_buttons = [
                InlineKeyboardButton(text="A", callback_data=f"answer:{question.id}:0"),
                InlineKeyboardButton(text="B", callback_data=f"answer:{question.id}:1"),
                InlineKeyboardButton(text="C", callback_data=f"answer:{question.id}:2"),
                InlineKeyboardButton(text="D", callback_data=f"answer:{question.id}:3"),
            ]

            hint_buttons = [
                InlineKeyboardButton(text="\uD83D\uDCB8 Застраховать сумму", callback_data=f"hint:hint_insure"),
                InlineKeyboardButton(text="\u274C Убрать два неправильных ответа", callback_data=f"hint:hint_remove_two"),
                InlineKeyboardButton(text="\uD83D\uDCB3 Забрать выигрыш", callback_data=f"hint:hint_take_money"),
            ]

            keyboard = InlineKeyboardMarkup(inline_keyboard=[
                answer_buttons[:2],
                answer_buttons[2:],
                hint_buttons
            ])

            # Отправляем сообщение с вопросом и ответами
            answers_text = "\n".join([
                f"A) {answers[0]}",
                f"B) {answers[1]}",
                f"C) {answers[2]}",
                f"D) {answers[3]}"
            ])

            await send_message(
                f"Вопрос {idx}: {question.question_text}\n\n{answers_text}",
                reply_markup=keyboard
            )

            try:
                callback_query = await wait_for_callback_query(user_id)
                if callback_query is None:
                    await send_message("Время вышло! Игра завершена.")
                    break

                logger.info(f"Callback data: {callback_query.data}")  # Логируем данные callback_query
                user_answer = callback_query.data.split(":")
            except Exception as e:
                logger.error(f"Ошибка при обработке callback_query: {e}")
                await send_message("Произошла ошибка. Попробуйте снова.")
                break

            if user_answer[0] == "hint":
                hint_key = user_answer[1]
                if hint_key == "hint_insure" and not hints_used["insure"]:
                    hints_used["insure"] = True
                    guaranteed_score = current_score
                    await send_message(f"Вы застраховали сумму: {guaranteed_score} баллов.")
                elif hint_key == "hint_remove_two" and not hints_used["remove_two"]:
                    hints_used["remove_two"] = True
                    wrong_answers = [ans for ans in answers if ans != question.correct_answer]
                    random.shuffle(wrong_answers)
                    updated_answers = [question.correct_answer, wrong_answers[0]]
                    random.shuffle(updated_answers)
                    await send_message(
                        f"Подсказка! Выберите правильный ответ:\n"
                        f"1) {updated_answers[0]}\n"
                        f"2) {updated_answers[1]}"
                    )
                elif hint_key == "hint_take_money" and not hints_used["take_money"]:
                    hints_used["take_money"] = True
                    if league_config["currency"] == "silver":
                        user.balance_silver += current_score
                    elif league_config["currency"] == "gold":
                        user.balance_gold += current_score
                    await session.commit()
                    await send_message(f"Вы забрали сумму: {current_score} баллов. Игра завершена.")
                    break
                else:
                    await send_message("Эта подсказка уже использована.")
                continue

            try:
                answer_index = int(user_answer[2])
                if answers[answer_index] == question.correct_answer:
                    current_score += SCORE_TABLE[idx - 1]
                    await send_message(f"Правильно! Ваши баллы: {current_score}")
                else:
                    await send_message(f"Неправильно. Правильный ответ: {question.correct_answer}")
                    break
            except (ValueError, IndexError):
                await send_message("Некорректный ответ. Попробуйте снова.")

        new_game.score = current_score
        if league_config["currency"] == "silver":
            user.balance_silver += guaranteed_score
        elif league_config["currency"] == "gold":
            user.balance_gold += guaranteed_score
        await session.commit()

        await send_message(f"Игра завершена. Ваши баллы: {current_score}")

    except SQLAlchemyError as e:
        await session.rollback()
        logger.error(f"Ошибка базы данных для пользователя {user_id}: {e}")
        await send_message("Ошибка базы данных.")
    except Exception as e:
        logger.error(f"Неожиданная ошибка для пользователя {user_id}: {e}")
        await send_message("Произошла ошибка.")
    finally:
        await session.close()


def shuffle_answers(correct_answer: str, incorrect_answers: list) -> list:
    """
    Перемешивает правильный и неправильные ответы.

    Args:
        correct_answer (str): Правильный ответ.
        incorrect_answers (list): Список неправильных ответов.

    Returns:
        list: Перемешанный список ответов.
    """
    answers = [correct_answer] + incorrect_answers
    random.shuffle(answers)
    return answers


def filter_answers(correct_answer: str, answers: list) -> list:
    """
    Удаляет два неправильных ответа.

    Args:
        correct_answer (str): Правильный ответ.
        answers (list): Список всех ответов.

    Returns:
        list: Список из двух ответов (правильный и один случайный неправильный).
    """
    incorrect_answers = [answer for answer in answers if answer != correct_answer]
    if len(incorrect_answers) > 1:
        incorrect_answers = random.sample(incorrect_answers, 1)
    return [correct_answer] + incorrect_answers
