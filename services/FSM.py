from aiogram.fsm.state import State, StatesGroup


class AddQuestionState(StatesGroup):
    waiting_for_league = State()
    waiting_for_level = State()
    waiting_for_question = State()
    waiting_for_correct_answer = State()
    waiting_for_option_2 = State()
    waiting_for_option_3 = State()
    waiting_for_option_4 = State()
    add_question = State()
    check_and_add_question = State()


class ProcessGameState(StatesGroup):
    waiting_for_question = State()  # Ожидание начала вопроса
    waiting_for_answer = State()  # Ожидание ответа от пользователя
    waiting_for_hint = State()  # Ожидание выбора подсказки
    game_finished = State()  # Завершение игры


# Создаем группу состояний для диалога
class DialogStates(StatesGroup):
    rating = State()  # Состояние для рейтинга


class ExchangeStates(StatesGroup):
    """Состояния для процесса обмена валют."""
    waiting_for_exchange_amount = State()


class ProposeQuestionState(StatesGroup):
    waiting_for_question_text = State()
    waiting_for_correct_answer = State()
    waiting_for_wrong_answer_1 = State()
    waiting_for_wrong_answer_2 = State()
    waiting_for_wrong_answer_3 = State()
    check_and_add_question = State()
