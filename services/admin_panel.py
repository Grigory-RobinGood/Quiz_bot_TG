from aiogram import Dispatcher, types
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext
from aiogram.filters import StateFilter

from db.models import add_question
from config_data.config import TgBot


# Команда для начала добавления вопроса (только для администратора)
# async def start_add_question(message: types.Message):
#     if message.from_user.id == ADMIN_ID:
#         await message.answer("Выберите уровень викторины (bronze/silver).")
#         #await AddQuestionState.waiting_for_level()
#     else:
#         await message.answer("У вас нет прав для добавления вопросов.")


# Получение уровня викторины (bronze/silver)
async def process_level(message: types.Message, state: FSMContext):
    level = message.text.lower()
    if level not in ['bronze', 'silver']:
        await message.answer("Неверный уровень. Пожалуйста, выберите 'bronze' или 'silver'.")
        return
    await state.update_data(level=level)
    await message.answer("Введите текст вопроса.")
    await AddQuestionState.waiting_for_question.set()


# Получение текста вопроса
async def process_question(message: types.Message, state: FSMContext):
    await state.update_data(question=message.text)
    await message.answer("Введите правильный ответ.")
    await AddQuestionState.waiting_for_correct_answer.set()


# Получение правильного ответа
async def process_correct_answer(message: types.Message, state: FSMContext):
    await state.update_data(correct_answer=message.text)
    await message.answer("Введите вариант ответа 1.")
    await AddQuestionState.waiting_for_option_1.set()


# Получение варианта ответа 1
async def process_option_1(message: types.Message, state: FSMContext):
    await state.update_data(option_1=message.text)
    await message.answer("Введите вариант ответа 2.")
    await AddQuestionState.waiting_for_option_2.set()


# Получение варианта ответа 2
async def process_option_2(message: types.Message, state: FSMContext):
    await state.update_data(option_2=message.text)
    await message.answer("Введите вариант ответа 3.")
    await AddQuestionState.waiting_for_option_3.set()


# Получение варианта ответа 3
async def process_option_3(message: types.Message, state: FSMContext):
    await state.update_data(option_3=message.text)
    await message.answer("Введите вариант ответа 4.")
    await AddQuestionState.waiting_for_option_4.set()


# Получение варианта ответа 4 и сохранение вопроса в базу данных
async def process_option_4(message: types.Message, state: FSMContext):
    await state.update_data(option_4=message.text)

    # Получаем все данные из состояния
    data = await state.get_data()
    await add_question(
        data['level'],
        data['question'],
        data['correct_answer'],
        data['option_1'],
        data['option_2'],
        data['option_3'],
        data['option_4']
    )
    await message.answer("Вопрос успешно добавлен!")
    await state.finish()


def register_admin_handlers(dp: Dispatcher):
    dp.message_handler(start_add_question, commands=['add_question'], state="*")
    dp.message_handler(process_level, state=AddQuestionState.waiting_for_level)
    dp.message_handler(process_question, state=AddQuestionState.waiting_for_question)
    dp.message_handler(process_correct_answer, state=AddQuestionState.waiting_for_correct_answer)
    dp.message_handler(process_option_1, state=AddQuestionState.waiting_for_option_1)
    dp.message_handler(process_option_2, state=AddQuestionState.waiting_for_option_2)
    dp.message_handler(process_option_3, state=AddQuestionState.waiting_for_option_3)
    dp.message_handler(process_option_4, state=AddQuestionState.waiting_for_option_4)
