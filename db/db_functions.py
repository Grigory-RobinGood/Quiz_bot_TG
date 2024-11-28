from db.models import Question
from sqlalchemy.orm import Session


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

