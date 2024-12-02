import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.filters import CommandStart
from aiogram.types import Message, ReplyKeyboardRemove
from aiogram.fsm.storage.redis import RedisStorage, Redis
from sqlalchemy.orm import Session
from db.models import Users
from db.models import SessionLocal
from db.db_functions import add_user_to_db

from config_data.config import Config, load_config
from handlers import admin_handlers, user_handlers
from keyboards.set_menu import set_main_menu
from lexicon.lexicon_ru import LEXICON_RU
from keyboards.keyboards import admin_kb, main_kb

# Инициализируем логгер
logger = logging.getLogger(__name__)


# Функция конфигурирования и запуска бота
async def main():
    # Конфигурируем логирование
    logging.basicConfig(
        level=logging.INFO,
        format='%(filename)s:%(lineno)d #%(levelname)-8s '
               '[%(asctime)s] - %(name)s - %(message)s')

    # Выводим в консоль информацию о начале запуска бота
    logger.info('Starting bot')

    # Загружаем конфиг в переменную config
    config: Config = load_config()

    # Инициализируем бот и диспетчер
    bot = Bot(
        token=config.tg_bot.token,
        default=DefaultBotProperties(parse_mode='HTML',
                                     protect_content=False)
    )

    # db_url = config.database.url  # Убедитесь, что путь совпадает с вашей конфигурацией
    # engine = create_engine(db_url, echo=True)

    redis = Redis(host='localhost')
    storage = RedisStorage(redis=redis)
    dp = Dispatcher(storage=storage)

    await set_main_menu(bot)

    @dp.message(CommandStart())
    async def process_start_command(message: Message):
        if message.from_user.id in config.tg_bot.admin_ids:
            await message.answer(text='Вы вошли в админ панель', reply_markup=admin_kb)

        else:
            await message.answer(text=LEXICON_RU['/start'], reply_markup=main_kb, parse_mode='HTML')


            # Создаем сессию базы данных
            session: Session = SessionLocal()

            try:
                # Проверяем, есть ли username (могут быть пользователи без него)
                username = message.from_user.username if message.from_user.username else "----"

                # Добавляем пользователя в базу
                add_user_to_db(
                    session=session,
                    user_id=message.from_user.id,
                    username=username,
                    league=1,
                    games=0,
                    balance_silver_coins=500,
                    balance_gold_coins=0,
                    balance_rub=0,
                    referrals=0
                )
            except Exception as e:
                # Логируем ошибку, если что-то пошло не так
                print(f"Ошибка при обработке команды /start: {e}")

            finally:
                # Закрываем сессию
                session.close()


    # Регистриуем роутеры в диспетчере
    dp.include_router(user_handlers.router)
    dp.include_router(admin_handlers.router)

    # Пропускаем накопившиеся апдейты и запускаем polling
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

asyncio.run(main())
