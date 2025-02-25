from aiogram import Router, F
from aiogram.types import CallbackQuery
from aiogram_dialog import Window, Dialog, DialogManager, StartMode
from aiogram_dialog.widgets.kbd import ScrollingGroup, Button
from aiogram_dialog.widgets.text import Format, Const

from keyboards.keyboards import account_kb
from services.FSM import DialogStates
from services.services import get_rating_data

rating_router = Router()


# Функция для кнопки "Назад"
async def go_back(callback: CallbackQuery, button: Button, dialog_manager: DialogManager):
    await callback.message.delete()  # Удаляем сообщение с рейтингом
    await dialog_manager.done()  # Закрываем диалог
    await callback.message.answer(text="Вы вошли в свой аккаунт", reply_markup=account_kb)

# Окно диалога
rating_window = Window(
    Format(
        "🏆 Недельный рейтинг:\n\n"
        "{league_ratings}\n\n"
        "❓ Рейтинг по предложенным вопросам:\n{question_rating}\n\n"
        "📢 Рейтинг по подпискам на каналы:\n{subscription_rating}\n\n"
        "👥 Рейтинг по приглашенным друзьям:\n{referral_rating}"
    ),
    ScrollingGroup(
        Button(Const("Назад"), id="back", on_click=go_back),
        id="scroll",
        width=1,
        height=10,
    ),
    state=DialogStates.rating,
    getter=get_rating_data,
)

# Создание диалога
rating_dialog = Dialog(rating_window)

# ✅ Регистрируем диалог в роутере
rating_router.include_routers(rating_dialog)

