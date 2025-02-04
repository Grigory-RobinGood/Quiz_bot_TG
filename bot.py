import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.filters import CommandStart
from aiogram.types import Message
from aiogram.fsm.storage.redis import RedisStorage, Redis
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.future import select

from db.models import AsyncSessionLocal, Users  # Импортируем вашу модель Users
from config_data.config import Config, load_config
from handlers import admin_handlers, user_handlers, game_handlers
from keyboards.set_menu import set_main_menu
from lexicon.lexicon_ru import LEXICON_RU
from keyboards.keyboards import admin_kb, main_kb
from middleware.game_mdwr import DatabaseMiddleware
from services import game
from db.models import async_session_maker

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

    redis = Redis(host='localhost')
    storage = RedisStorage(redis=redis)
    dp = Dispatcher(storage=storage)

    await set_main_menu(bot)

    @dp.message(CommandStart())
    async def process_start_command(message: Message):
        """
        Обработчик команды /start. Добавляет нового пользователя в базу данных, если его там ещё нет.
        """
        # Проверяем, является ли пользователь администратором
        if message.from_user.id in config.tg_bot.admin_ids:
            await message.answer(text='Вы вошли в админ панель', reply_markup=admin_kb)
            return

        # Приветствие для обычных пользователей
        await message.answer(text=LEXICON_RU['/start'], reply_markup=main_kb, parse_mode='HTML')

        # Создаем сессию базы данных
        async with AsyncSessionLocal() as session:
            try:
                # Получаем user_id и username пользователя или устанавливаем значение по умолчанию
                user_id = message.from_user.id
                username = message.from_user.username or "unknown_user"

                # Проверяем, есть ли пользователь в базе
                result = await session.execute(select(Users).filter_by(user_id=user_id))
                user = result.scalars().first()

                if not user:
                    # Если пользователя нет, добавляем его в базу данных
                    new_user = Users(user_id=user_id, username=username)
                    session.add(new_user)
                    await session.commit()
                    logger.info("Пользователь успешно добавлен: %s", username)
                else:
                    logger.info("Пользователь уже существует: %s", username)

            except SQLAlchemyError as e:
                # Логируем ошибки базы данных
                logger.error("Ошибка при добавлении пользователя в базу данных: %s", e)
                await message.answer("Произошла ошибка при регистрации. Попробуйте позже.")

            except Exception as e:
                # Логируем другие возможные ошибки
                logger.error("Ошибка при обработке команды /start: %s", e)

    # Регистриуем роутеры в диспетчере
    dp.include_router(user_handlers.router)
    dp.include_router(admin_handlers.router)
    dp.include_router(game_handlers.router)
    dp.include_router(game.router)

    #Регистрируем middleware
    dp.update.middleware(DatabaseMiddleware(async_session_maker))

    logging.basicConfig(level=logging.DEBUG)
    # Пропускаем накопившиеся апдейты и запускаем polling
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

asyncio.run(main())
