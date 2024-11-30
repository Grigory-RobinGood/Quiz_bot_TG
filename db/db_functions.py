from sqlalchemy import BigInteger
from sqlalchemy.orm import Session

from db.models import Question, Users


#________________ Функция для добавления вопроса в базу данных_____________________________
def add_question_to_db(session: Session, league: str, level: str, question: str,
                       correct_answer: str, answer_2: str, answer_3: str, answer_4: str):
    try:
        # Создаем объект вопроса
        new_question = Question(
            league=league,
            level=level,
            question=question,
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


# ____________________Функция для добавления пользователя в базу данных______________________________
def add_user_to_db(session: Session, user_id: int, username: str, league: int = 0,
                   games: int = 0, balance_silver_coins: int = 0, balance_gold_coins: int = 0,
                   balance_rub: int = 0, referrals: int = 0):
    try:
        # Проверяем, есть ли пользователь в базе
        existing_user = session.query(Users).filter(Users.user_id == user_id).first()
        if existing_user:
            print(f"Пользователь с user_id {user_id} уже существует.")
            return

        # Создаем нового пользователя
        new_user = Users(
            user_id=user_id,
            username=username,
            league=league,
            games=games,
            balance_silver_coins=balance_silver_coins,
            balance_gold_coins=balance_gold_coins,
            balance_rub=balance_rub,
            referrals=referrals
        )

        # Добавляем пользователя в сессию
        session.add(new_user)

        # Фиксируем изменения
        session.commit()

        print("Пользователь успешно добавлен")

    except Exception as e:
        session.rollback()  # Откатываем изменения в случае ошибки
        print(f"Ошибка при добавлении пользователя в базу данных: {e}")
