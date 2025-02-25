import logging
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session
from sqlalchemy.sql.expression import func
from sqlalchemy.exc import SQLAlchemyError

from db.models import Question, Users

# Логирование
logger = logging.getLogger(__name__)


def add_question_to_db(session: Session, league: str, difficulty: str, question_text: str,
                       correct_answer: str, answer_2: str, answer_3: str, answer_4: str):
    """
    Добавляет новый вопрос в таблицу `questions`.

    :param session: SQLAlchemy Session
    :param league: Лига вопроса (Bronze, Silver, Gold)
    :param difficulty: Сложность вопроса (Easy, Medium, Hard)
    :param question_text: Текст вопроса
    :param correct_answer: Правильный ответ
    :param answer_2: Второй вариант ответа
    :param answer_3: Третий вариант ответа
    :param answer_4: Четвёртый вариант ответа
    """
    try:
        # Проверяем, существует ли вопрос с таким текстом
        existing_question = session.query(Question).filter_by(question_text=question_text).first()
        if existing_question:
            logger.warning("Вопрос с таким текстом уже существует: %s", question_text)
            return "Вопрос уже существует"

        # Создаем объект вопроса
        new_question = Question(
            league=league,
            difficulty=difficulty,
            question_text=question_text,
            correct_answer=correct_answer,
            answer_2=answer_2,
            answer_3=answer_3,
            answer_4=answer_4
        )

        # Добавляем в сессию и коммитим
        session.add(new_question)
        session.commit()
        logger.info("Вопрос успешно добавлен: %s", question_text)
        return "Вопрос успешно добавлен"

    except SQLAlchemyError as e:
        # Откатываем изменения в случае ошибки
        session.rollback()
        logger.error("Ошибка при добавлении вопроса: %s", e)
        return f"Ошибка: {e}"


# _______________ Функция для добавления пользователя в базу данных _______________
def add_user_to_db(session: Session, user_id: int, username: str):
    """
    Добавляет нового пользователя в таблицу `users`, если пользователь с таким именем ещё не существует.

    :param session: SQLAlchemy Session
    :param user_id: user_id пользователя (уникальное  значение)
    :param username: Имя пользователя (уникальное значение)
    :return: Строка с результатом операции
    """
    try:
        # Проверяем, есть ли пользователь с таким user_id
        existing_user = session.query(Users).filter_by(user_id=user_id).first()
        if existing_user:
            logger.info("Пользователь с id %s уже существует.", user_id)
            return f"Пользователь с id '{user_id}' уже существует."

        # Создаем нового пользователя
        new_user = Users(user_id=user_id, username=username)

        # Добавляем в сессию и сохраняем изменения
        session.add(new_user)
        session.commit()
        logger.info("Новый пользователь добавлен: %s", username)
        return f"Пользователь '{username}' успешно добавлен."

    except SQLAlchemyError as e:
        # Откатываем изменения в случае ошибки
        session.rollback()
        logger.error("Ошибка при добавлении пользователя: %s", e)
        return f"Ошибка: {e}"


# __________ Получение вопросов из базы (в случайном порядке) _______________
async def get_question(league: str, session: AsyncSession):
    """
    Получение списка вопросов для заданной лиги.

    Args:
        league (str): Лига ("Bronze", "Silver", "Gold").
        session (AsyncSession): Асинхронная сессия SQLAlchemy.

    Returns:
        list: Список вопросов.
    """
    questions = []
    for difficulty in ["Easy", "Medium", "Hard"]:
        result = await session.execute(
            select(Question)
            .where(Question.league == league, Question.difficulty == difficulty)
            .order_by(func.random())
            .limit(5)
        )
        questions.extend(result.scalars().all())

    return [
        {
            "id": question.id,
            "text": question.question_text,
            "answers": [
                question.correct_answer,
                question.answer_2,
                question.answer_3,
                question.answer_4,
            ],
            "correct_answer": question.correct_answer,
            "difficulty": question.difficulty,
            "score": 10 if question.difficulty == "Easy" else 20 if question.difficulty == "Medium" else 30,
        }
        for question in questions
    ]


#______Обновление баланса пользователя после игры____________
async def update_user_balance(user_id: int, amount: int, currency: str, session: AsyncSession):
    """
    Обновление баланса пользователя.

    Args:
        user_id (int): ID пользователя.
        amount (int): Сумма для добавления или снятия.
        currency (str): Тип валюты ("silver" или "gold").
        session (AsyncSession): Асинхронная сессия SQLAlchemy.

    Returns:
        bool: True, если успешно, иначе False.
    """
    result = await session.execute(select(Users).where(Users.user_id == user_id))
    user = result.scalars().first()

    if not user:
        return False

    if currency == "bronze":
        user.balance_bronze += amount
    elif currency == "silver":
        user.balance_silver += amount
    elif currency == "gold":
        user.balance_gold += amount

    await session.commit()
    return True
