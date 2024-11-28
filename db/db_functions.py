from db.models import Question
from sqlalchemy.orm import Session


def add_question_to_db(session: Session, league: str, level: str, question: str,
                       correct_option: str, option_2: str, option_3: str, option_4: str):
    try:
        # Создаем объект вопроса
        new_question = Question(
            league=league,
            level=level,
            question=question,
            correct_option=correct_option,
            option_1=correct_option,  # Основной правильный вариант как option_1
            option_2=option_2,
            option_3=option_3,
            option_4=option_4
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

