import asyncio
import logging
import os

from aiocache import RedisCache
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.filters import CommandStart
from aiogram.fsm.storage.base import DefaultKeyBuilder
from aiogram.types import Message
from aiogram.fsm.storage.redis import RedisStorage, Redis
from aiogram_dialog import setup_dialogs
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from sqlalchemy.future import select

from db.models import AsyncSessionLocal, Users, user_referrals  # Импортируем вашу модель Users
from config_data.config import Config, load_config
from handlers import admin_handlers, user_handlers, game_handlers
from handlers.user_handlers import exchange_router
from keyboards.set_menu import set_main_menu
from lexicon.lexicon_ru import LEXICON_RU
from keyboards.keyboards import admin_kb, main_kb
from middleware.game_mdwr import DatabaseMiddleware
from services import game, user_dialog
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
    storage = RedisStorage(redis=redis, key_builder=DefaultKeyBuilder(with_destiny=True))

    REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
    REDIS_PORT = int(os.getenv("REDIS_PORT", 6379))

    # Инициализация кеша
    cache = RedisCache(endpoint=REDIS_HOST, port=REDIS_PORT)

    dp = Dispatcher(storage=storage)

    await set_main_menu(bot)

    @dp.message(CommandStart())
    async def process_start_command(message: Message):
        """
        Обработчик команды /start. Добавляет нового пользователя в базу данных, если его там ещё нет.
        Также обрабатывает реферальную систему.
        """
        user_id = message.from_user.id
        username = message.from_user.username or "unknown_user"

        # Проверяем, является ли пользователь администратором
        if user_id in config.tg_bot.admin_ids:
            await message.answer(text='Вы вошли в админ панель', reply_markup=admin_kb)
            return

        # Разбираем аргументы команды (реферальный код)
        args = message.text.split()
        referrer_id = None

        if len(args) > 1 and args[1].isdigit():
            referrer_id = int(args[1])
            if referrer_id == user_id:  # Запрещаем приглашать самого себя
                referrer_id = None

        async with AsyncSessionLocal() as session:
            try:
                # Проверяем, есть ли пользователь в базе
                result = await session.execute(select(Users).filter_by(user_id=user_id))
                user = result.scalars().first()

                if not user:
                    # Добавляем нового пользователя
                    new_user = Users(user_id=user_id, username=username)
                    session.add(new_user)
                    await session.commit()
                    logger.info("Пользователь успешно добавлен: %s", username)

                    # Обрабатываем реферальную систему
                    if referrer_id:
                        # Проверяем, не зарегистрирован ли пользователь уже как реферал
                        existing_referral = await session.execute(
                            select(user_referrals).where(user_referrals.c.referred_id == new_user.id)
                        )

                        if not existing_referral.scalars().first():
                            # Получаем пригласившего пользователя
                            referrer = await session.execute(select(Users).where(Users.user_id == referrer_id))
                            referrer = referrer.scalars().first()

                            if referrer:
                                try:
                                    # Добавляем запись в user_referrals
                                    session.execute(user_referrals.insert().values(
                                        referrer_id=referrer.id, referred_id=new_user.id
                                    ))

                                    # Начисляем бонусы
                                    referrer.balance_silver += 500
                                    new_user.balance_silver += 500

                                    await session.commit()

                                    # Уведомляем пригласившего
                                    await message.bot.send_message(
                                        referrer.user_id,
                                        f"🎉 Ваш друг {message.from_user.full_name} присоединился к игре!\n"
                                        f"Вы получили 500 серебряных монет! 💰"
                                    )

                                    await message.answer(
                                        f"🎉 Вы зарегистрировались по ссылке друга!\n"
                                        f"Вы и ваш друг получили 500 серебряных монет! 💰\n"
                                        f"Проверьте свой баланс и присоединяйтесь к игре!"
                                    )

                                except IntegrityError:
                                    await session.rollback()

                else:
                    logger.info("Пользователь уже существует: %s", username)
                # Приветствие для обычных пользователей
                await message.answer(text=LEXICON_RU['/start'], reply_markup=main_kb, parse_mode='HTML')
            except SQLAlchemyError as e:
                logger.error("Ошибка при работе с БД: %s", e)
                await message.answer("⚠ Произошла ошибка при регистрации. Попробуйте позже.")
            except Exception as e:
                logger.error("Ошибка в обработке команды /start: %s", e)

    # Регистрируем диалоги
    setup_dialogs(dp)

    # Регистриуем роутеры в диспетчере
    dp.include_router(user_handlers.router)
    dp.include_router(exchange_router)
    dp.include_router(admin_handlers.router)
    dp.include_router(game_handlers.router)
    dp.include_router(game.router)
    dp.include_router(user_dialog.rating_router)

    # Регистрируем middleware
    dp.update.middleware(DatabaseMiddleware(async_session_maker))

    logging.basicConfig(level=logging.DEBUG)
    # Пропускаем накопившиеся апдейты и запускаем polling
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot, skip_updates=True)


if __name__ == "__main__":
    asyncio.run(main())
