import random
import logging

from aiogram import F, Router, Bot, types
from aiogram.types import Message, ReplyKeyboardRemove, CallbackQuery

from db.models import AsyncSessionLocal, Users
from keyboards.keyboards import main_kb
from lexicon.lexicon_ru import LEXICON_RU
from services import filters as f, game
from services.filters import StartGameCallbackData
from services.game import start_game

router = Router()
logger = logging.getLogger(__name__)


# Этот хэндлер срабатывает на команду /help
@router.callback_query(f.HelpCallbackData.filter())
async def process_help_command(message: Message):
    await message.answer(text=LEXICON_RU['/help'], reply_markup=main_kb)


#______________________Хэндлеры для БРОНЗОВОЙ ЛИГИ___________________________________
# Хэндлер для нажатия на кнопку "Бронзовая лига" на главной клавиатуре
@router.callback_query(StartGameCallbackData.filter())
async def handle_bronze_league_start(call: CallbackQuery, callback_data: StartGameCallbackData, bot: Bot):
    """
    Обработчик нажатия кнопки "Бронзовая лига".
    """
    # Проверяем значение лиги
    if callback_data.league == "Bronze":
        league = callback_data.league
        user_id = call.from_user.id

        async with AsyncSessionLocal() as session:
            try:
                # Отправляем сообщение о начале игры
                await call.message.edit_reply_markup()  # Убираем клавиатуру из сообщения
                await call.message.answer(f"Игра в {league} лиге начинается!")

                # Вызываем функцию старта игры
                await start_game(
                    session=session,
                    user_id=user_id,
                    league=league,
                    send_message=call.message.answer,
                    router=game.router
                )

            except Exception as e:
                # Логируем ошибку и отправляем пользователю сообщение
                logger.error(f"Ошибка при запуске игры: {e}")
                await call.message.answer("Произошла ошибка при запуске игры. Попробуйте позже.")





#_______________________________________СЕРЕБРЯННАЯ ЛИГА____________________________________________
# Константы и глобальные переменные
# scores_silver = [5, 10, 15, 20, 25, 50, 75, 100, 125, 150, 200, 250, 300, 400, 500]
# user_silver_games = {}
#
# # Подсказки
# HINTS = {
#     "remove_wrong": "Убрать неверный ответ",
#     "insurance": "Застраховать",
#     "second_chance": "Право на ошибку",
#     "take_prize": "Забрать приз"
# }
#
#
# async def finish_game(message: Message, user_id: int):
#     """
#     Завершает игру, отображает итоговый результат и добавляет его к текущему балансу пользователя в базе данных.
#     """
#     game = user_silver_games.pop(user_id, None)  # Удаляем состояние игры пользователя
#     if not game:
#         await message.answer("Ошибка: Игра не найдена.")
#         return
#
#         # Итоговый результат
#     final_score = game["score"]
#
#     # Обновляем результат в базе данных
#     session = SessionLocal()
#     try:
#         user = session.query(Users).filter(Users.user_id == user_id).first()
#         if user:
#             # Добавляем результат к текущему значению
#             user.balance_gold_coins += final_score
#         else:
#             # Если пользователя нет в базе, создаем запись с текущим результатом
#             new_user = Users(
#                 user_id=user_id,
#                 balance_gold_coins=final_score
#             )
#             session.add(new_user)
#         session.commit()
#     finally:
#         session.close()
#
#     # Отправляем сообщение об окончании игры
#     await message.answer(f"Игра окончена! Ваш итоговый результат: {final_score} очков.\n"
#                          f"Общий результат: {user.silver_league_score if user else final_score} очков.")
#
#
# @router.message(F.text == LEXICON_RU['silver_league'])
# async def process_game(message: Message, bot: Bot):
#     session = SessionLocal()
#     try:
#         hide_message = await message.answer(".", reply_markup=ReplyKeyboardRemove())
#         await bot.delete_message(chat_id=hide_message.chat.id, message_id=hide_message.message_id)
#
#         # Получаем вопросы
#         questions = []
#         questions.extend(get_questions(session, "silver", "level_1", 5))
#         questions.extend(get_questions(session, "silver", "level_2", 5))
#         questions.extend(get_questions(session, "silver", "level_3", 5))
#
#         if len(questions) < 15:
#             await message.answer("Ошибка: недостаточно вопросов для игры.")
#             return
#
#         # Сохраняем состояние игры пользователя
#         user_silver_games[message.from_user.id] = {
#             "questions": questions,
#             "current_index": 0,
#             "score": 0,
#             "insurance_score": None,
#             "second_chance": False,
#             "shuffled_answers": {},
#             "hints": HINTS.copy()
#         }
#
#         # Отправляем первый вопрос
#         await send_question(message, message.from_user.id)
#     finally:
#         session.close()
#
#
# async def send_question(message: Message, user_id: int):
#     """
#     Отправляет пользователю следующий вопрос.
#     """
#     game = user_silver_games.get(user_id)
#     if not game:
#         await message.answer("Ошибка: Игра не найдена.")
#         return
#
#     current_index = game["current_index"]
#     if current_index >= len(game["questions"]):
#         await finish_game(message, user_id)
#         return
#
#     question = game["questions"][current_index]
#     options = [question.correct_answer, question.answer_2, question.answer_3, question.answer_4]
#     random.shuffle(options)
#
#     # Сохраняем перемешанные варианты
#     game["shuffled_answers"][question.id] = options
#
#     # Генерация клавиатуры
#     keyboard = generate_game_keyboard(question.id, options, game["hints"])
#
#     await message.answer(
#         text=f"Вопрос {current_index + 1}:\n{question.question}",
#         reply_markup=keyboard
#     )


# @router.callback_query(F.data.startswith("answer:"))
# async def process_answer(callback: CallbackQuery):
#     """
#     Обрабатывает выбор ответа.
#     """
#     user_id = callback.from_user.id
#     game = user_silver_games.get(user_id)
#     if not game:
#         await callback.answer("Ошибка: Игра не найдена.")
#         return
#
#     data = callback.data.split(":")
#     question_id = int(data[1])
#     user_answer_index = int(data[2]) - 1
#
#     options = game["shuffled_answers"].get(question_id, [])
#     correct_answer = game["questions"][game["current_index"]].correct_answer
#
#     if not options:
#         await callback.answer("Ошибка: варианты ответа не найдены.")
#         return
#
#     user_answer = options[user_answer_index]
#     if user_answer == correct_answer:
#         game["score"] += scores_silver[game["current_index"]]
#         await callback.answer("Верно!")
#         game["current_index"] += 1
#         await callback.message.delete()
#         await send_question(callback.message, user_id)
#     else:
#         if game["second_chance"]:
#             # Право на ошибку
#             game["second_chance"] = False
#             options.remove(user_answer)  # Убираем неправильный вариант
#             keyboard = generate_game_keyboard(question_id, options, game["hints"])
#             await callback.message.edit_text(
#                 text=f"Попробуйте еще раз:\n{game['questions'][game['current_index']].question}",
#                 reply_markup=keyboard
#             )
#         else:
#             await callback.answer("Неверно. Игра окончена.")
#             await finish_game(callback.message, user_id)
#
#
# @router.callback_query(F.data.startswith("hint:"))
# async def process_hint(callback: CallbackQuery):
#     """
#     Обрабатывает использование подсказок.
#     """
#     user_id = callback.from_user.id
#     game = user_silver_games.get(user_id)
#     if not game:
#         await callback.answer("Ошибка: Игра не найдена.")
#         return
#
#     hint_key = callback.data.split(":")[1]
#
#     if hint_key == "remove_wrong":
#         options = game["shuffled_answers"][game["questions"][game["current_index"]].id]
#         correct_answer = game["questions"][game["current_index"]].correct_answer
#         options = [opt for opt in options if opt != correct_answer][:3] + [correct_answer]
#         random.shuffle(options)
#         keyboard = generate_game_keyboard(game["questions"][game["current_index"]].id, options, game["hints"])
#         game["hints"].pop("remove_wrong")
#         await callback.message.edit_reply_markup(reply_markup=keyboard)
