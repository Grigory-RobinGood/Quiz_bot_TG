import logging

from aiogram.types import CallbackQuery
from aiogram.filters.callback_data import CallbackData
from aiogram.filters import BaseFilter


logging.basicConfig(level=logging.INFO)


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


class Level1CallbackData(CallbackData, prefix="Easy"):
    pass


class Level2CallbackData(CallbackData, prefix="Medium"):
    pass


class Level3CallbackData(CallbackData, prefix="Hard"):
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


class CancelGameCallbackData(CallbackData, prefix="cancel_game"):
    pass


class UserRateCallbackData(CallbackData, prefix="user_rate"):
    pass


class MagazineCallbackData(CallbackData, prefix="magazine"):
    pass


class EarnCoinsCallbackData(CallbackData, prefix="earn_coins"):
    pass


class BalanceCallbackData(CallbackData, prefix="balance"):
    pass


class ExchangeCallbackData(CallbackData, prefix="exchange"):
    pass


class AddBalanceCallbackData(CallbackData, prefix="add_balance"):
    pass


class OutBalanceCallbackData(CallbackData, prefix="out_balance"):
    pass


class SuggestQuestionCallbackData(CallbackData, prefix="suggest_question"):
    pass


class SubscribeCallbackData(CallbackData, prefix="subscribe"):
    pass


class AccountCallbackData(CallbackData, prefix="account"):
    pass


class HelpCallbackData(CallbackData, prefix="help"):
    pass


class StartGameCallbackData(CallbackData, prefix="start_game"):
    league: str

    def __post_init__(self):
        print(f"Создан callback_data: {self.pack()}")  # Логируем формирование callback_data


#Фукция ожидания ответа от пользователя
class CallbackQueryFilter(BaseFilter):
    def __init__(self, user_id: int):
        self.user_id = user_id

    async def __call__(self, callback_query: CallbackQuery) -> bool:
        return callback_query.from_user.id == self.user_id
