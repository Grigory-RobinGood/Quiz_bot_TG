import random
import logging

from string import ascii_uppercase

from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

from lexicon.lexicon_ru import LEXICON_RU
from services import filters as f
from services.filters import StartGameCallbackData, ExchangeCallbackData

logger = logging.getLogger(__name__)

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

# _________________Создаем клавиатуру выбора сложности вопроса______________
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
                              callback_data="add"),
         ],
        [InlineKeyboardButton(text=LEXICON_RU['cancel'],
                              callback_data="cancel"),
         ]
    ]
)

# --------------------- Создаем клавиатуры для user -------------------------------------------------
# ------------ Создаем главную клавиатуру через InlineKeyboardMarkup --------------------------

main_kb = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(
                text="Бронзовая лига",
                callback_data=StartGameCallbackData(league="Bronze").pack()
            ),
            InlineKeyboardButton(
                text="Серебряная лига",
                callback_data=StartGameCallbackData(league="Silver").pack()
            ),
            InlineKeyboardButton(
                text="Золотая лига",
                callback_data=StartGameCallbackData(league="Gold").pack()
            ),
        ],
        [
            InlineKeyboardButton(
                text="Аккаунт",
                callback_data=f.AccountCallbackData().pack()
            ),
            InlineKeyboardButton(
                text="Справка",
                callback_data=f.HelpCallbackData().pack()
            ),
        ]
    ]
)

# ____________Создаем инлайн клавиатуру для меню аккаунт____________
account_kb = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text='Рейтинг',
                              callback_data="user_rate"),
         InlineKeyboardButton(text='Баланс',
                              callback_data=f.BalanceCallbackData().pack()),
         InlineKeyboardButton(text='Обмен',
                              callback_data=f.ExchangeButtonCallbackData().pack())
         ],
        [InlineKeyboardButton(text='Заработать монеты',
                              callback_data=f.EarnCoinsCallbackData().pack())
         ]
    ]
)


# ____________Создаем инлайн клавиатуру для меню баланс____________
def get_balance_keyboard():
    keyboard = InlineKeyboardBuilder()
    keyboard.button(text="➕ Пополнить", callback_data="top_up_balance")
    keyboard.button(text="➖ Вывести", callback_data="withdrawal")
    keyboard.button(text="🔄 Обменять", callback_data=f.ExchangeButtonCallbackData().pack())
    keyboard.button(text="🔙 Назад", callback_data="back_to_account")
    return keyboard.as_markup()


# ____________Создаем инлайн клавиатуру для меню заработать____________
earn_coins_kb = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="💡 Предложить свой вопрос", callback_data="propose_question")],
    [InlineKeyboardButton(text="📢 Подписаться на спонсоров", callback_data="subscribe_sponsors")],
    [InlineKeyboardButton(text="👥 Пригласить друга", callback_data="invite_friend")],
    [InlineKeyboardButton(text="🔙 Назад", callback_data="back_to_account")]
])

# ____________Создаем инлайн клавиатуру для меню обмен____________
exchange_kb = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text='RUB → Gold',
                              callback_data=ExchangeCallbackData(from_currency="Rubles", to_currency="Gold").pack()),
         InlineKeyboardButton(text='Gold → RUB',
                              callback_data=ExchangeCallbackData(from_currency="Gold", to_currency="Rubles").pack())],

        [InlineKeyboardButton(text='Gold → Silver',
                              callback_data=ExchangeCallbackData(from_currency="Gold", to_currency="Silver").pack()),
         InlineKeyboardButton(text='Silver → Gold',
                              callback_data=ExchangeCallbackData(from_currency="Silver", to_currency="Gold").pack())],

        [InlineKeyboardButton(text='Назад',
                              callback_data="back_to_account")]
    ]
)

# Клавиатура для отмены обмена
cancel_exchange_kb = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="❌ Отмена", callback_data="cancel_exchange")]
    ]
)

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


# ___________Генерация инлайн-клавиатуры с вариантами ответов__________
def generate_shuffled_keyboard(question_id: int, options: list[str]) -> tuple[InlineKeyboardMarkup, list[str]]:
    shuffled_options = options.copy()
    random.shuffle(shuffled_options)  # Перемешиваем варианты ответа
    builder = InlineKeyboardBuilder()
    for i, option in enumerate(shuffled_options, start=1):
        builder.button(text=option, callback_data=f"answer:{question_id}:{i}")
    return builder.as_markup(), shuffled_options


# _____________Генерация игровой клавиатуры__________________


def create_question_keyboard(question_id: int, answers: list, hints: dict) -> InlineKeyboardMarkup:
    """
    Создаёт клавиатуру для вопроса.

    Args:
        question_id (int): ID вопроса.
        answers (list): Список ответов.
        hints (dict): Подсказки, формат {'hint_key': 'Название подсказки'}.

    Returns:
        InlineKeyboardMarkup: Сгенерированная клавиатура.
    """
    keyboard = InlineKeyboardMarkup(inline_keyboard=[])

    # Добавляем ответы (по два в строке)
    buttons = [
        InlineKeyboardButton(text=f"{chr(65 + idx)}", callback_data=f"answer:{question_id}:{idx}")
        for idx, _ in enumerate(answers)
    ]
    for i in range(0, len(buttons), 2):
        keyboard.inline_keyboard.append(buttons[i:i + 2])

    # Добавляем подсказки (в одну строку)
    hint_buttons = [
        InlineKeyboardButton(text=name, callback_data=f"hint:{hint_key}")
        for hint_key, name in hints.items()
    ]
    keyboard.inline_keyboard.append(hint_buttons)

    return keyboard


def generate_game_message(question_text, answers):
    """
    Формирует текст сообщения с вопросом и вариантами ответов.

    Args:
        question_text (str): Текст вопроса.
        answers (list): Список ответов.

    Returns:
        str: Текст сообщения.
    """
    letters = list(ascii_uppercase[:len(answers)])
    formatted_answers = "\n".join(
        [f"{letter}. {answer}" for letter, answer in zip(letters, answers)]
    )
    return f"{question_text}\n\n{formatted_answers}"
