import random
import logging

from aiogram import Router
from aiogram.fsm.context import FSMContext
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from sqlalchemy.sql.expression import func
from sqlalchemy.future import select
from sqlalchemy.exc import SQLAlchemyError

from db.models import Users, Game, Question
from services.FSM import ProcessGameState

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


def question_to_dict(question: Question) -> dict:
    """
    Преобразует объект Question в словарь.

    Args:
        question (Question): Объект вопроса.

    Returns:
        dict: Словарь с данными вопроса.
    """
    return {
        "id": question.id,
        "question_text": question.question_text,
        "correct_answer": question.correct_answer,
        "incorrect_answers": [question.answer_2, question.answer_3, question.answer_4],
        "score": SCORE_TABLE[0]  # Пример, добавьте логику для определения баллов
    }


async def start_game(session, user_id: int, league: str, send_message, router, state: FSMContext):
    """
    Запуск игры для пользователя.

    Args:
        session: Асинхронная сессия SQLAlchemy.
        user_id (int): ID пользователя.
        league (str): Лига игры ('Bronze', 'Silver', 'Gold').
        send_message (callable): Функция для отправки сообщений пользователю.
        router (Router): Router для обработки временных callback-хендлеров.
        state (FSMContext): Контекст состояния.
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
            questions += [question_to_dict(q) for q in result.scalars().all()]  # Преобразуем вопросы в словари

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

        # Инициализация состояния
        await state.update_data(
            questions=questions,
            current_score=current_score,
            hints_used=hints_used
        )

        # Отправляем первый вопрос
        await send_next_question(send_message, state)

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


async def send_next_question(send_message, state: FSMContext, success_message: str = None):
    """
    Отправляет следующий вопрос пользователю.

    Args:
        send_message (callable): Функция для отправки сообщений.
        state (FSMContext): Контекст состояния.
        success_message (str, optional): Сообщение о правильном ответе.
    """
    data = await state.get_data()
    questions = data.get("questions", [])
    question_index = data.get("question_index", 0)

    # Проверяем, остались ли вопросы
    if not questions:
        current_score = data.get("current_score", 0)
        await send_message(f"Игра завершена! Ваш итоговый счёт: {current_score}.")
        await state.clear()
        return

    # Если есть success_message, сначала отправляем его
    if success_message:
        await send_message(success_message)

    # Берём следующий вопрос
    current_question = questions.pop(0)
    correct_answer = current_question["correct_answer"]
    incorrect_answers = current_question["incorrect_answers"]
    answers = [correct_answer] + incorrect_answers
    random.shuffle(answers)  # Перемешиваем ответы

    # Сохраняем данные в состоянии
    await state.update_data(
        questions=questions,
        current_question=current_question,
        answers=answers,
        question_index=question_index,
    )

    # Создаём клавиатуру с вариантами ответов
    answer_buttons = [
        InlineKeyboardButton(text="A", callback_data=f"answer:{current_question['id']}:0"),
        InlineKeyboardButton(text="B", callback_data=f"answer:{current_question['id']}:1"),
        InlineKeyboardButton(text="C", callback_data=f"answer:{current_question['id']}:2"),
        InlineKeyboardButton(text="D", callback_data=f"answer:{current_question['id']}:3"),
    ]
    hint_buttons = [
        InlineKeyboardButton(text="\uD83D\uDCB8 Застраховать сумму", callback_data=f"hint:hint_insure"),
        InlineKeyboardButton(text="\u274C Убрать два неправильных ответа", callback_data=f"hint:hint_remove_two"),
        InlineKeyboardButton(text="\uD83D\uDCB3 Забрать выигрыш", callback_data=f"hint:hint_take_money"),
    ]
    keyboard = InlineKeyboardMarkup(inline_keyboard=[answer_buttons[:2], answer_buttons[2:], hint_buttons])

    # Отправляем вопрос пользователю
    await send_message(
        f"Вопрос: {current_question['question_text']}\n\n"
        f"A) {answers[0]}\n"
        f"B) {answers[1]}\n"
        f"C) {answers[2]}\n"
        f"D) {answers[3]}",
        reply_markup=keyboard
    )
    await state.set_state(ProcessGameState.waiting_for_answer)
