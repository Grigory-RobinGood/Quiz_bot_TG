import os
from dataclasses import dataclass
from environs import Env


@dataclass
class TgBot:
    token: str  # Токен для доступа к телеграм-боту
    admin_ids: list[int]  # Список id администраторов бота


@dataclass
class DbURL:
    url: str  # URL для базы данных


@dataclass
class Config:
    tg_bot: TgBot
    database: DbURL


def load_config(path: str = None) -> Config:
    env = Env()
    env.read_env(path)

    return Config(
        tg_bot=TgBot(
            token=env.str("BOT_TOKEN"),
            admin_ids=list(map(int, env.list("ADMIN_IDS", subcast=str)))
        ),
        database=DbURL(
            url=env.str("DATABASE_URL")
        )
    )


PAY_TOKEN = str(os.getenv("TELEGRAM_PAY_TOKEN"))
SHOP_ID = str(os.getenv('YOOKASSA_SHOP_ID'))
SECRET_KEY = str(os.getenv('YOOKASSA_SECRET_KEY'))
