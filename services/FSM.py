from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import default_state, State, StatesGroup
from aiogram.fsm.storage.redis import RedisStorage, Redis


class AddQuestionState(StatesGroup):
    waiting_for_league = State()
    waiting_for_level = State()
    waiting_for_question = State()
    waiting_for_correct_answer = State()
    waiting_for_option_2 = State()
    waiting_for_option_3 = State()
    waiting_for_option_4 = State()
    add_question = State()

