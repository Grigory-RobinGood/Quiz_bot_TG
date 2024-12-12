import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.filters import CommandStart
from aiogram.types import Message, ReplyKeyboardRemove
from aiogram.fsm.storage.redis import RedisStorage, Redis
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError

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


    # engine = create_engine(db_url, echo=True)

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
        session: Session = SessionLocal()

        try:
            # Получаем username пользователя или устанавливаем значение по умолчанию
            username = message.from_user.username or "unknown_user"

            # Добавляем пользователя в базу данных
            result = add_user_to_db(session=session, username=username)

            # Логируем и отправляем сообщение пользователю, если необходимо
            logger.info("Результат добавления пользователя: %s", result)

        except SQLAlchemyError as e:
            # Логируем ошибки базы данных
            logger.error("Ошибка при добавлении пользователя в базу данных: %s", e)
            await message.answer("Произошла ошибка при регистрации. Попробуйте позже.")

        except Exception as e:
            # Логируем другие возможные ошибки
            logger.error("Ошибка при обработке команды /start: %s", e)

        finally:
            # Закрываем сессию базы данных
            session.close()


    # Регистриуем роутеры в диспетчере
    dp.include_router(user_handlers.router)
    dp.include_router(admin_handlers.router)

    # Пропускаем накопившиеся апдейты и запускаем polling
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

asyncio.run(main())
