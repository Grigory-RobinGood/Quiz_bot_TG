from sqlalchemy import BigInteger
from sqlalchemy.orm import Session
from sqlalchemy.sql.expression import func

from db.models import Question, User


# ____________ Функция для добавления вопроса в базу данных _______________
def add_question_to_db(session: Session, league: str, difficulty: str, question_text: str,
                       correct_answer: str, answer_2: str, answer_3: str, answer_4: str):
    try:
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

        # Добавляем в сессию
        session.add(new_question)

        # Фиксируем изменения в базе
        session.commit()

        print("Вопрос успешно добавлен в базу данных.")

    except Exception as e:
        session.rollback()  # Откатываем изменения в случае ошибки
        print(f"Ошибка при добавлении вопроса в базу данных: {e}")

    finally:
        session.close()  # Закрываем сессию


# _______________ Функция для добавления пользователя в базу данных _______________
def add_user_to_db(session: Session, username: str):
    try:
        # Проверяем, есть ли пользователь в базе
        existing_user = session.query(User).filter(User.username == username).first()
        if existing_user:
            print(f"Пользователь с username {username} уже существует.")
            return

        # Создаем нового пользователя
        new_user = User(
            username=username
        )

        # Добавляем пользователя в сессию
        session.add(new_user)

        # Фиксируем изменения
        session.commit()

        print("Пользователь успешно добавлен.")

    except Exception as e:
        session.rollback()  # Откатываем изменения в случае ошибки
        print(f"Ошибка при добавлении пользователя в базу данных: {e}")

    finally:
        session.close()  # Закрываем сессию


# __________ Получение вопросов из базы (в случайном порядке) _______________
def get_questions(session: Session, league: str, difficulty: str, limit: int):
    return (
        session.query(Question)
        .filter_by(league=league, difficulty=difficulty)
        .order_by(func.random())  # Случайный порядок
        .limit(limit)
        .all()
    )
