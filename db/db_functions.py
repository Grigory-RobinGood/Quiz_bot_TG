import logging
from sqlalchemy import BigInteger
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
def add_user_to_db(session: Session, username: str):
    """
    Добавляет нового пользователя в таблицу `users`, если пользователь с таким именем ещё не существует.

    :param session: SQLAlchemy Session
    :param username: Имя пользователя (уникальное значение)
    :return: Строка с результатом операции
    """
    try:
        # Проверяем, есть ли пользователь с таким именем
        existing_user = session.query(Users).filter_by(username=username).first()
        if existing_user:
            logger.warning("Пользователь с именем %s уже существует.", username)
            return f"Пользователь с username '{username}' уже существует."

        # Создаем нового пользователя
        new_user = Users(username=username)

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
def get_questions(session: Session, league: str, difficulty: str, limit: int):
    return (
        session.query(Question)
        .filter_by(league=league, difficulty=difficulty)
        .order_by(func.random())  # Случайный порядок
        .limit(limit)
        .all()
    )
