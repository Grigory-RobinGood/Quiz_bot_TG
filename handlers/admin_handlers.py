from aiogram import Router
from aiogram.types import Message
from aiogram.fsm.state import default_state, State, StatesGroup
from aiogram.filters import StateFilter, callback_data
from aiogram.fsm.storage.redis import RedisStorage, Redis
from aiogram.types import CallbackQuery
from aiogram.fsm.context import FSMContext

from db.db_functions import add_question_to_db
from services.FSM import AddQuestionState
from lexicon.lexicon_ru import LEXICON_RU
from keyboards.keyboards import admin_kb_league, admin_kb_select_level, add_or_cancel
from services import filters as f
from db.models import SessionLocal

router = Router()
session = SessionLocal()


# ------------Обрабатываем нажатие кнопки "добавить вопрос"---------------
@router.callback_query(f.AddQuestionCallbackData.filter())
async def add_question(call: CallbackQuery, state: FSMContext):
    # Ответ пользователю
    await call.message.answer(text=LEXICON_RU['send_league'], reply_markup=admin_kb_league)
    await call.answer()  # Закрываем всплывающее уведомление Telegram
    await state.set_state(AddQuestionState.waiting_for_league)  # Устанавливаем состояние для добавления вопроса

#  Разобраться с коллбэк дата
#__Выбираем Лигу в которую хотим добавить вопрос__
@router.callback_query(AddQuestionState.waiting_for_league)
async def send_league(call: CallbackQuery, state: FSMContext):
    await state.update_data(league=str(callback_data))  # Запоминаем какую лигу выбрали
    await call.message.answer(text=LEXICON_RU['send_level_question'], reply_markup=admin_kb_select_level)
    await call.answer()  # Закрываем всплывающее уведомление Telegram
    await state.set_state(AddQuestionState.waiting_for_level)


#__Выбираем уровень сложности вопроса (1, 2 или 3)__
@router.callback_query(AddQuestionState.waiting_for_level)
async def send_level(call: CallbackQuery, state: FSMContext):
    await state.update_data(level=str(callback_data))  # Запоминаем какой уровень выбрали
    await call.message.answer(text=LEXICON_RU['write_your_question'])
    await call.answer()  # Закрываем всплывающее уведомление Telegram
    await state.set_state(AddQuestionState.waiting_for_question)


#__Пишем вопрос для добавления в базу вопросов__
@router.message(AddQuestionState.waiting_for_question)
async def enter_question(message: Message, state: FSMContext):
    await state.update_data(question=str(message.text))  # Запоминаем вопрос
    await message.answer(text=LEXICON_RU['correct_answer'])
    await state.set_state(AddQuestionState.waiting_for_correct_answer)


#__Пишем правильный ответ для добавления в базу __
@router.message(AddQuestionState.waiting_for_correct_answer)
async def enter_correct_answer(message: Message, state: FSMContext):
    await state.update_data(correct_answer=str(message.text))  # Запоминаем правильный ответ
    await message.answer(text=LEXICON_RU['answer_var2'])
    await state.set_state(AddQuestionState.waiting_for_option_2)


#__Пишем второй вариант ответа для добавления в базу __
@router.message(AddQuestionState.waiting_for_option_2)
async def enter_answer_var2(message: Message, state: FSMContext):
    await state.update_data(answer_var2=str(message.text))  # Запоминаем второй вариант ответа
    await message.answer(text=LEXICON_RU['answer_var3'])
    await state.set_state(AddQuestionState.waiting_for_option_3)


#__Пишем третий вариант ответа для добавления в базу __
@router.message(AddQuestionState.waiting_for_option_3)
async def enter_answer_var3(message: Message, state: FSMContext):
    await state.update_data(answer_var3=str(message.text))  # Запоминаем третий вариант ответа
    await message.answer(text=LEXICON_RU['answer_var4'])
    await state.set_state(AddQuestionState.waiting_for_option_4)


#__Пишем четвертый вариант ответа для добавления в базу __
@router.message(AddQuestionState.waiting_for_option_4)
async def enter_answer_var4(message: Message, state: FSMContext):
    await state.update_data(answer_var4=str(message.text))  # Запоминаем четвертый вариант ответа
    await message.answer(text=LEXICON_RU['add_question?'], reply_markup=add_or_cancel)
    await state.set_state(AddQuestionState.add_question)


#__Обрабатываем нажатие на кнопку "Добавить"
@router.callback_query(AddQuestionState.add_question)
async def question_added(call: CallbackQuery, state: FSMContext):
    # Получаем данные из машины состояний
    data = await state.get_data()

    # Извлекаем переменные из состояния
    league = data.get("league", "Не указана лига")
    level = data.get("level", "Не указан уровень")
    question = data.get("question", "Не указан вопрос")
    correct_answer = data.get("correct_answer", "Не указан правильный вариант")
    answer_2 = data.get("answer_2", "Не указан вариант 2")
    answer_3 = data.get("answer_3", "Не указан вариант 3")
    answer_4 = data.get("answer_4", "Не указан вариант 4")

    # Вывод сообщения с собранными данными
    await call.message.answer(
        text=f"{LEXICON_RU['question_added']}\n"
             f"Лига: {league}\n"
             f"Уровень: {level}\n"
             f"Вопрос: {question}\n"
             f"Правильный ответ: {correct_answer}"
             f"2. {answer_2}\n"
             f"3. {answer_3}\n"
             f"4. {answer_4}\n"
    )

    # Запуск функции добавления в базу данных
    try:
        await add_question_to_db(
            session=session,
            league=league,
            level=level,
            question=question,
            correct_answer=correct_answer,
            answer_2=answer_2,
            answer_3=answer_3,
            answer_4=answer_4,
        )

        await call.message.answer(text=LEXICON_RU['db_success'])  # Сообщение об успехе
    except Exception as e:
        await call.message.answer(
            text=f"{LEXICON_RU['db_error']} {str(e)}"  # Сообщение об ошибке
        )

    # Сбрасываем состояние
    await state.clear()

    # Закрываем уведомление
    await call.answer()


# ------------Обрабатываем нажатие кнопки "показать статистику"-------------
@router.callback_query(f.ShowStatisticCallbackData.filter())
async def handle_show_statistic(call: CallbackQuery):
    await call.message.answer(text=LEXICON_RU['bot_statistics'])
    await call.answer()


# ------------Обрабатываем нажатие кнопки "отправить рассылку"--------------
@router.callback_query(f.SendMessageCallbackData.filter())
async def handle_show_statistic(call: CallbackQuery):
    await call.message.answer(text=LEXICON_RU['write_your_message'])
    await call.answer()


# ------------Обрабатываем нажатие кнопки "редактирование квиза"------------
@router.callback_query(f.EditQuizCallbackData.filter())
async def handle_show_statistic(call: CallbackQuery):
    await call.message.answer(text=LEXICON_RU['edit_quiz'])
    await call.answer()


# -------------Обрабатываем нажатие кнопки "назад"---------------------------
@router.callback_query(f.BackCallbackData.filter())
async def handle_show_statistic(call: CallbackQuery):
    await call.message.answer(text=LEXICON_RU['back'])
    await call.answer()


# Хэндлер для сообщений, которые не попали в другие хэндлеры
@router.message()
async def send_answer(message: Message):
    await message.answer(text=LEXICON_RU['other_answer'])
