from aiogram.types import CallbackQuery
from aiogram.filters.callback_data import CallbackData


class AddQuestionCallbackData(CallbackData, prefix="add_question"):
    pass


class ShowStatisticCallbackData(CallbackData, prefix="show_statistic"):
    pass


class SendMessageCallbackData(CallbackData, prefix="send_message"):
    pass


class EditQuizCallbackData(CallbackData, prefix="edit_quiz"):
    pass


class BackCallbackData(CallbackData, prefix="back"):
    pass


class BronzeLeagueCallbackData(CallbackData, prefix="bronze_league"):
    pass


class SilverLeagueCallbackData(CallbackData, prefix="silver_league"):
    pass


class GoldLeagueCallbackData(CallbackData, prefix="gold_league"):
    pass


class Level1CallbackData(CallbackData, prefix="level_1"):
    pass


class Level2CallbackData(CallbackData, prefix="level_2"):
    pass


class Level3CallbackData(CallbackData, prefix="level_3"):
    pass


class AddCallbackData(CallbackData, prefix="add"):
    pass


class CancelCallbackData(CallbackData, prefix="cancel"):
    pass
