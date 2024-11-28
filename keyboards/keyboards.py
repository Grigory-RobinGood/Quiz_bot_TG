from aiogram.filters.callback_data import CallbackData
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import ReplyKeyboardBuilder, InlineKeyboardBuilder
from lexicon.lexicon_ru import LEXICON_RU, LEXICON_COMMANDS_RU
from services import filters as f



# ------- Создаем клавиатуру через ReplyKeyboardBuilder -------

# Создание кнопок
bronze_league = KeyboardButton(text=LEXICON_RU['bronze_league'])
silver_league = KeyboardButton(text=LEXICON_RU['silver_league'])
gold_league = KeyboardButton(text=LEXICON_RU['gold_league'])
account = KeyboardButton(text=LEXICON_RU['account'])
suggest_question = KeyboardButton(text=LEXICON_RU['suggest_question'])
balance = KeyboardButton(text=LEXICON_RU['balance'])
bn_help = KeyboardButton(text=LEXICON_RU['bn_help'])

# _____________Создаем главную клавиатуру___________________________________________
main_kb = ReplyKeyboardMarkup(
    keyboard=[
        [bronze_league, silver_league, gold_league],  # Первая строка
        [account, suggest_question],  # Вторая строка
        [balance, bn_help]  # Третья строка
    ],
    resize_keyboard=True  # Уменьшает кнопки
)

# -------------Создаем клавиатуры админа--------------------------

# Создаем главную клавиатуру админа
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

# Создаем клавиатуру выбора лиги
admin_kb_league = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text=LEXICON_RU['bronze_league'],
                              callback_data=f.BronzeLeagueCallbackData().pack()),
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

#Создаем клавиатуру выбора сложности вопроса
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


# Создаем клавиатуру для добавления или отмены
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

# ------- Создаем игровую клавиатуру без использования билдера -------

# Создаем кнопки игровой клавиатуры бронзовой лиги
bn_delete_answer1 = KeyboardButton(text=LEXICON_RU['delete_answer'])
bn_insurance = KeyboardButton(text=LEXICON_RU['insurance'])
bn_mistake = KeyboardButton(text=LEXICON_RU['mistake'])
bn_take_prize = KeyboardButton(text=LEXICON_RU['take_prize'])

# Создаем клавиатуру с кнопками для бронзовой лиги
game_kb_bronze = ReplyKeyboardMarkup(
    keyboard=[[bn_delete_answer1],
              [bn_insurance],
              [bn_mistake],
              [bn_take_prize]],
    resize_keyboard=True)

# Создаем кнопки игровой клавиатуры серебряной лиги
bn_delete_answer2 = KeyboardButton(text=LEXICON_RU['delete_answer'])
bn_insurance = KeyboardButton(text=LEXICON_RU['insurance'])
bn_mistake = KeyboardButton(text=LEXICON_RU['mistake'])
bn_take_prize = KeyboardButton(text=LEXICON_RU['take_prize'])

# Создаем клавиатуру с кнопками для серебряной лиги
game_kb_silver = ReplyKeyboardMarkup(
    keyboard=[[bn_delete_answer2],
              [bn_insurance],
              [bn_mistake],
              [bn_take_prize]],
    resize_keyboard=True)
