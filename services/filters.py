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


class ACallbackData(CallbackData, prefix="A"):
    pass


class BCallbackData(CallbackData, prefix="B"):
    pass


class CCallbackData(CallbackData, prefix="C"):
    pass


class DCallbackData(CallbackData, prefix="D"):
    pass


class DelAnswerCallbackData(CallbackData, prefix="del_answer"):
    pass


class InsuranceCallbackData(CallbackData, prefix="insurance"):
    pass


class MistakeCallbackData(CallbackData, prefix="mistake"):
    pass


class TakePrizeCallbackData(CallbackData, prefix="take_prize"):
    pass


