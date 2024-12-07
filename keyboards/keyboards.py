import random
from typing import Tuple, List

from aiogram.filters.callback_data import CallbackData
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import ReplyKeyboardBuilder, InlineKeyboardBuilder
from lexicon.lexicon_ru import LEXICON_RU, LEXICON_COMMANDS_RU
from services import filters as f

# ------------ Создаем главную клавиатуру через ReplyKeyboardBuilder --------------------------
# Создание кнопок
bronze_league = KeyboardButton(text=LEXICON_RU['bronze_league'])
silver_league = KeyboardButton(text=LEXICON_RU['silver_league'])
gold_league = KeyboardButton(text=LEXICON_RU['gold_league'])
account = KeyboardButton(text=LEXICON_RU['account'])
suggest_question = KeyboardButton(text=LEXICON_RU['suggest_question'])
balance = KeyboardButton(text=LEXICON_RU['balance'])
bn_help = KeyboardButton(text=LEXICON_RU['bn_help'])

main_kb = ReplyKeyboardMarkup(
    keyboard=[
        [bronze_league, silver_league, gold_league],  # Первая строка
        [account, suggest_question],  # Вторая строка
        [balance, bn_help]  # Третья строка
    ],
    resize_keyboard=True  # Уменьшает кнопки
)

# -----------------Создаем клавиатуры админа---------------------------------------

# ______Создаем главную клавиатуру админа_______________
admin_kb = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text=LEXICON_RU['add_question'],
                              callback_data=f.AddQuestionCallbackData().pack()),
         ],
        [InlineKeyboardButton(text=LEXICON_RU['show_statistic'],
                              callback_data=f.ShowStatisticCallbackData().pack()),
         ],
        [InlineKeyboardButton(text=LEXICON_RU['send_message'],
                              callback_data=f.SendMessageCallbackData().pack()),
         ],
        [InlineKeyboardButton(text=LEXICON_RU['edit_quiz'],
                              callback_data=f.EditQuizCallbackData().pack()),
         ],
        [InlineKeyboardButton(text=LEXICON_RU['back'],
                              callback_data=f.BackCallbackData().pack()),
         ]
    ]
)

# _____________Создаем клавиатуру выбора лиги__________-
admin_kb_league = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text=LEXICON_RU['bronze_league'],
                              callback_data='bronze'),
         ],
        [InlineKeyboardButton(text=LEXICON_RU['silver_league'],
                              callback_data=f.SilverLeagueCallbackData().pack()),
         ],
        [InlineKeyboardButton(text=LEXICON_RU['gold_league'],
                              callback_data=f.GoldLeagueCallbackData().pack()),
         ],
        [InlineKeyboardButton(text=LEXICON_RU['cancel'],
                              callback_data=f.BackCallbackData().pack()),
         ],
    ]
)

#_________________Создаем клавиатуру выбора сложности вопроса______________
admin_kb_select_level = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text=LEXICON_RU['level_1'],
                              callback_data=f.Level1CallbackData().pack()),
         ],
        [InlineKeyboardButton(text=LEXICON_RU['level_2'],
                              callback_data=f.Level2CallbackData().pack()),
         ],
        [InlineKeyboardButton(text=LEXICON_RU['level_3'],
                              callback_data=f.Level3CallbackData().pack()),
         ],
        [InlineKeyboardButton(text=LEXICON_RU['cancel'],
                              callback_data=f.BackCallbackData().pack()),
         ]
    ]
)

# ___________Создаем клавиатуру для добавления или отмены____________________
add_or_cancel = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text=LEXICON_RU['add'],
                              callback_data=f.AddCallbackData().pack()),
         ],
        [InlineKeyboardButton(text=LEXICON_RU['cancel'],
                              callback_data=f.CancelCallbackData().pack()),
         ]
    ]
)

# --------------------- Создаем клавиатуры user -------------------------------------------------

# ____________Создаем главную игровую клавиатуру____________________
game_kb = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text='A',
                              callback_data=f.ACallbackData().pack()),
         InlineKeyboardButton(text='B',
                              callback_data=f.BCallbackData().pack()),
         InlineKeyboardButton(text='C',
                              callback_data=f.CCallbackData().pack()),
         InlineKeyboardButton(text='D',
                              callback_data=f.DCallbackData().pack())
         ],
        [InlineKeyboardButton(text=LEXICON_RU['delete_answer'],
                              callback_data=f.DelAnswerCallbackData().pack()),
         InlineKeyboardButton(text=LEXICON_RU['insurance'],
                              callback_data=f.InsuranceCallbackData().pack()),
         InlineKeyboardButton(text=LEXICON_RU['mistake'],
                              callback_data=f.MistakeCallbackData().pack()),
         InlineKeyboardButton(text=LEXICON_RU['take_prize'],
                              callback_data=f.TakePrizeCallbackData().pack())
         ]
    ]
)

# ____________Создаем клавиатуру запуска игры___________________
start_game = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text=LEXICON_RU['start_game'],
                              callback_data=f.StartGameCallbackData().pack()),
         ],
        [InlineKeyboardButton(text=LEXICON_RU['cancel'],
                              callback_data=f.CancelGameCallbackData().pack()),
         ]
    ]
)


# ___________Генерация инлайн-клавиатуры с вариантами ответов__________
def generate_shuffled_keyboard(question_id: int, options: list[str]) -> tuple[InlineKeyboardMarkup, list[str]]:
    shuffled_options = options.copy()
    random.shuffle(shuffled_options)  # Перемешиваем варианты ответа
    builder = InlineKeyboardBuilder()
    for i, option in enumerate(shuffled_options, start=1):
        builder.button(text=option, callback_data=f"answer:{question_id}:{i}")
    return builder.as_markup(), shuffled_options


# _____________Генерация игровой клавиатуры__________________
def generate_game_keyboard(question_id, options, hints):
    """
    Генерирует клавиатуру с вариантами ответа (A, B, C, D) и подсказками.
    """
    keyboard = InlineKeyboardMarkup()


    # Генерация вариантов ответа с буквами
    letters = ['A', 'B', 'C', 'D']
    for idx, option in enumerate(options):
        keyboard.add(InlineKeyboardButton(
            text=f"{letters[idx]}. {option}",
            callback_data=f"answer:{question_id}:{idx + 1}"
        ))

    # Добавление подсказок
    if hints:
        hint_buttons = [
            InlineKeyboardButton(
                text=hint_text,
                callback_data=f"hint:{hint_key}"  # Формат: hint:<ключ подсказки>
            ) for hint_key, hint_text in hints.items()
        ]
        keyboard.row(*hint_buttons)

    return keyboard

