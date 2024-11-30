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

# ____________Создаем кнопки главной игровой клавиатуры____________________
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
