import os
import logging
from sqlalchemy import (
    Column, Integer, String, ForeignKey, Boolean, Float, DateTime, Enum, Table, create_engine
)
from sqlalchemy.orm import relationship, declarative_base, sessionmaker
from sqlalchemy.sql import func
from config_data.config import Config, load_config

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

engine = create_engine(DATABASE_URL, echo=True)
SessionLocal = sessionmaker(bind=engine)

Base = declarative_base()

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
    username = Column(String(50), unique=True, nullable=False)
    balance_rubles = Column(Float, default=0.0)
    balance_silver = Column(Integer, default=0)
    balance_gold = Column(Integer, default=0)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.timezone('UTC', func.now()))

    games = relationship('Game', back_populates='user')
    referrals = relationship('User', secondary=user_referrals,
                             primaryjoin=id == user_referrals.c.referrer_id,
                             secondaryjoin=id == user_referrals.c.referred_id,
                             backref='referred_by')
    subscriptions = relationship('SponsorChannel', secondary=user_subscriptions,
                                 back_populates='subscribers')


class BaseQuestion(Base):
    __abstract__ = True

    id = Column(Integer, primary_key=True, autoincrement=True)
    question_text = Column(String(500), unique=True, nullable=False)
    correct_answer = Column(String(100), nullable=False)
    answer_2 = Column(String(100), nullable=False)
    answer_3 = Column(String(100), nullable=False)
    answer_4 = Column(String(100), nullable=False)
    difficulty = Column(Enum('Easy', 'Medium', 'Hard', name='difficulty_enum'), nullable=False)
    league = Column(Enum('Bronze', 'Silver', 'Gold', name='league_enum'), nullable=False)


class Question(BaseQuestion):
    __tablename__ = 'questions'


class ProposedQuestion(BaseQuestion):
    __tablename__ = 'proposed_questions'

    created_by_user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.timezone('UTC', func.now()))
    user = relationship('User', back_populates='proposed_questions')


class Game(Base):
    __tablename__ = 'games'

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    league = Column(Enum('Bronze', 'Silver', 'Gold', name='league_enum'), nullable=False)
    score = Column(Integer, default=0)
    created_at = Column(DateTime(timezone=True), server_default=func.timezone('UTC', func.now()))
    finished_at = Column(DateTime, nullable=True)

    user = relationship('User', back_populates='games')


# Таблица каналов-спонсоров
class SponsorChannel(Base):
    __tablename__ = 'sponsor_channels'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), nullable=False)
    link = Column(String(255), nullable=False)

    # Связь
    subscribers = relationship(
        'User',
        secondary=user_subscriptions,
        back_populates='subscriptions'
    )


# Таблица транзакций (оплаты выигрыша, покупки монет)
class Transaction(Base):
    __tablename__ = 'transactions'

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    amount = Column(Float, nullable=False)  # Сумма транзакции
    currency = Column(String(50), nullable=False)  # Тип валюты (рубли, серебро, золото)
    transaction_type = Column(String(50), nullable=False)  # Например, покупка, вывод
    created_at = Column(DateTime(timezone=True), server_default=func.timezone('UTC', func.now()))

    # Связь
    user = relationship('User', back_populates='transactions')


# Добавляем связь с транзакциями к пользователям
Users.transactions = relationship('Transaction', back_populates='user')

Base.metadata.create_all(engine)

#  _______________________Код для SQLite____________________________

# import os
#
# from sqlalchemy import Column, Integer, String, create_engine, BigInteger
# from sqlalchemy.orm import DeclarativeBase, sessionmaker
#
# # Создаем директорию для базы данных, если её нет
# os.makedirs("db", exist_ok=True)
#
# # Создаем подключение к базе данных
# DATABASE_URL = "sqlite:///db/quiz_db.sqlite"
# engine = create_engine(DATABASE_URL, echo=True)
#
# # Создаем фабрику для сессий
# SessionLocal = sessionmaker(bind=engine)
#
#
# # Новый базовый класс для моделей
# class Base(DeclarativeBase):
#     pass
#
#
# # Модель для таблицы вопросов
# class Question(Base):
#     __tablename__ = "questions"
#
#     id = Column(Integer, primary_key=True, autoincrement=True)
#     league = Column(String, nullable=False)  # Лига (Bronze, Silver, Gold)
#     level = Column(String, nullable=False)  # Уровень сложности (Easy, Medium, Hard)
#     question = Column(String, nullable=False)
#     correct_answer = Column(String, nullable=False)
#     answer_2 = Column(String, nullable=False)
#     answer_3 = Column(String, nullable=False)
#     answer_4 = Column(String, nullable=False)
#
#
# class Users(Base):
#     __tablename__ = "users"
#
#     id = Column(Integer, primary_key=True, autoincrement=True)
#     user_id = Column(BigInteger, nullable=False, unique=True)  # уникальное поле
#     username = Column(String, nullable=True)
#     league = Column(Integer, nullable=False, default=1)
#     games = Column(Integer, nullable=False, default=0)
#     balance_silver_coins = Column(Integer, nullable=False, default=500)
#     balance_gold_coins = Column(Integer, nullable=False, default=0)
#     balance_rub = Column(Integer, nullable=False, default=0)
#     referrals = Column(Integer, nullable=False, default=0)
#
#
# # Инициализация базы данных
# Base.metadata.create_all(bind=engine)
