from aiogram import F, Router
from aiogram.filters import Command
from aiogram.types import Message

from keyboards.keyboards import main_kb, game_kb
from lexicon.lexicon_ru import LEXICON_RU


router = Router()


# Этот хэндлер срабатывает на команду /help
@router.message(Command(commands='/help'))
async def process_help_command(message: Message):
    await message.answer(text=LEXICON_RU['/help'], reply_markup=main_kb)


# Этот хэндлер срабатывает на согласие пользователя играть в бронзовой лиге
@router.message(F.text == LEXICON_RU['bronze_league'] or
                F.text == LEXICON_RU['silver_league'] or
                F.text == LEXICON_RU['gold_league'])
async def process_game(message: Message):
    await message.answer(text=LEXICON_RU['yes'], reply_markup=game_kb)



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
