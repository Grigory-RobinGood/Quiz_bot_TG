import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart
from aiogram.types import Message
from aiogram.fsm.storage.redis import RedisStorage, Redis
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from config_data.config import Config, load_config, DbURL
from handlers import admin_handlers, user_handlers
from keyboards.set_menu import set_main_menu
from db.models import Base
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
        default=DefaultBotProperties(parse_mode='MarkdownV2',
                                     protect_content=False)
    )

    # db_url = config.database.url  # Убедитесь, что путь совпадает с вашей конфигурацией
    # engine = create_engine(db_url, echo=True)

    redis = Redis(host='localhost')
    storage = RedisStorage(redis=redis)
    dp = Dispatcher(storage=storage)

    await set_main_menu(bot)

    # Этот хэндлер срабатывает на команду /start
    @dp.message(CommandStart())
    async def process_start_command(message: Message):
        if message.from_user.id in config.tg_bot.admin_ids:
            await message.answer(text='Вы вошли в админ панель', reply_markup=admin_kb)

        else:
            await message.answer(text=LEXICON_RU['/start'], reply_markup=main_kb, parse_mode='HTML')

    # Регистриуем роутеры в диспетчере
    dp.include_router(user_handlers.router)
    dp.include_router(admin_handlers.router)

    # Пропускаем накопившиеся апдейты и запускаем polling
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

    # Создание таблиц
    #Base.metadata.create_all(bind=engine)


asyncio.run(main())
