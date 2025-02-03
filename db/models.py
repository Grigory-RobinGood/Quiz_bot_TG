import os
import logging
from sqlalchemy import (
    Column, Integer, String, ForeignKey, Boolean, Float, DateTime, Enum, Table, func
)
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import relationship, declarative_base, sessionmaker
from enum import Enum as PyEnum
from config_data.config import Config, load_config

# Загрузка конфигурации
config: Config = load_config()

# Логирование
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Директория для базы данных
os.makedirs("db", exist_ok=True)

# Подключение к базе данных
DATABASE_URL = config.database.url  # Убедитесь, что путь совпадает с вашей конфигурацией
if not DATABASE_URL:
    raise ValueError("DATABASE_URL is not set in the config.")

# Создаем асинхронный движок и сессию
engine = create_async_engine(DATABASE_URL, echo=True)
AsyncSessionLocal = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

# 🔹 Создаем фабрику сессий
async_session_maker = async_sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)

Base = declarative_base()


# Классы для Enum
class DifficultyEnum(PyEnum):
    Easy = 'Easy'
    Medium = 'Medium'
    Hard = 'Hard'


class LeagueEnum(PyEnum):
    Bronze = 'Bronze'
    Silver = 'Silver'
    Gold = 'Gold'


# Ассоциативные таблицы
user_referrals = Table(
    'user_referrals', Base.metadata,
    Column('referrer_id', Integer, ForeignKey('users.id'), primary_key=True),
    Column('referred_id', Integer, ForeignKey('users.id'), primary_key=True)
)

user_subscriptions = Table(
    'user_subscriptions', Base.metadata,
    Column('user_id', Integer, ForeignKey('users.id'), primary_key=True),
    Column('sponsor_channel_id', Integer, ForeignKey('sponsor_channels.id'), primary_key=True)
)


# Модели
class Users(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, unique=True, nullable=False)
    username = Column(String(50), nullable=True)
    balance_rubles = Column(Float, default=0.0)
    balance_silver = Column(Integer, default=0)
    balance_gold = Column(Integer, default=0)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.timezone('UTC', func.now()))

    games = relationship('Game', back_populates='user')
    referrals = relationship('Users', secondary=user_referrals,
                             primaryjoin=id == user_referrals.c.referrer_id,
                             secondaryjoin=id == user_referrals.c.referred_id,
                             backref='referred_by')
    subscriptions = relationship('SponsorChannel', secondary=user_subscriptions,
                                 back_populates='subscribers')
    proposed_questions = relationship('ProposedQuestion', back_populates='user')


class BaseQuestion(Base):
    __abstract__ = True

    id = Column(Integer, primary_key=True, autoincrement=True)
    question_text = Column(String(500), unique=True, nullable=False)
    correct_answer = Column(String(100), nullable=False)
    answer_2 = Column(String(100), nullable=False)
    answer_3 = Column(String(100), nullable=False)
    answer_4 = Column(String(100), nullable=False)
    difficulty = Column(Enum(DifficultyEnum, name='difficulty_enum'), nullable=False)
    league = Column(Enum(LeagueEnum, name='league_enum'), nullable=False)


class Question(BaseQuestion):
    __tablename__ = 'questions'


class ProposedQuestion(BaseQuestion):
    __tablename__ = 'proposed_questions'

    created_by_user_id = Column(Integer, ForeignKey('users.user_id'), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.timezone('UTC', func.now()))
    user = relationship('Users', back_populates='proposed_questions')


class Game(Base):
    __tablename__ = 'games'

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('users.user_id'), nullable=False)
    league = Column(Enum(LeagueEnum, name='league_enum'), nullable=False)
    score = Column(Integer, default=0)
    created_at = Column(DateTime(timezone=True), server_default=func.timezone('UTC', func.now()))
    finished_at = Column(DateTime, nullable=True)

    user = relationship('Users', back_populates='games')


class SponsorChannel(Base):
    __tablename__ = 'sponsor_channels'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), nullable=False)
    link = Column(String(255), nullable=False)

    subscribers = relationship(
        'Users',
        secondary=user_subscriptions,
        back_populates='subscriptions'
    )


class Transaction(Base):
    __tablename__ = 'transactions'
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('users.user_id'), nullable=False)
    amount = Column(Float, nullable=False)
    currency = Column(String(50), nullable=False)
    transaction_type = Column(String(50), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.timezone('UTC', func.now()))

    user = relationship('Users', back_populates='transactions')


# Добавляем связь с транзакциями к пользователям
Users.transactions = relationship('Transaction', back_populates='user')


# Асинхронное создание таблиц
async def create_tables():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


if __name__ == "__main__":
    import asyncio

    asyncio.run(create_tables())
