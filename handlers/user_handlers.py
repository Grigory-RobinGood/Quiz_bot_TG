from aiogram import F, Router, Bot
from aiogram.filters import Command
from aiogram.types import Message, ReplyKeyboardRemove

from keyboards.keyboards import main_kb, game_kb, start_game
from lexicon.lexicon_ru import LEXICON_RU

router = Router()


# Этот хэндлер срабатывает на команду /help
@router.message(Command(commands='/help'))
async def process_help_command(message: Message):
    await message.answer(text=LEXICON_RU['/help'], reply_markup=main_kb)


# Этот хэндлер срабатывает на согласие пользователя играть в бронзовой лиге
@router.message(F.text == LEXICON_RU['bronze_league'])
async def process_game(message: Message, bot: Bot):
    # Отправляем нейтральное сообщение для скрытия клавиатуры
    hide_message = await message.answer(".", reply_markup=ReplyKeyboardRemove())
    # Удаляем это сообщение
    await bot.delete_message(chat_id=hide_message.chat.id, message_id=hide_message.message_id)
    await message.answer(text=LEXICON_RU['welcome_bronze_league'], reply_markup=start_game)



# Этот хэндлер срабатывает на согласие пользователя играть в серебрянной лиге
@router.message(F.text == LEXICON_RU['silver_league'])
async def process_game(message: Message):
    await message.answer(text=LEXICON_RU['welcome_silver_league'], reply_markup=game_kb)


# Этот хэндлер срабатывает на согласие пользователя играть в золотой лиге
@router.message(F.text == LEXICON_RU['gold_league'])
async def process_game(message: Message):
    await message.answer(text=LEXICON_RU['welcome_gold_league'], reply_markup=game_kb)

# Этот хэндлер срабатывает на отказ пользователя играть в игру
# @router.message(F.text == LEXICON_RU['no_button'])
# async def process_no_answer(message: Message):
#     await message.answer(text=LEXICON_RU['no'])
#
#
# # Этот хэндлер срабатывает на любую из игровых кнопок
# @router.message(F.text.in_([LEXICON_RU['rock'],
#                             LEXICON_RU['paper'],
#                             LEXICON_RU['scissors']]))
# async def process_game_button(message: Message):
#     bot_choice = get_bot_choice()
#     await message.answer(text=f'{LEXICON_RU["bot_choice"]} '
#                               f'- {LEXICON_RU[bot_choice]}')
#     winner = get_winner(message.text, bot_choice)
#     await message.answer(text=LEXICON_RU[winner], reply_markup=main_kb)
