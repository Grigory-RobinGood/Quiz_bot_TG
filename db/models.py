import os

from sqlalchemy import Column, Integer, String, create_engine, BigInteger
from sqlalchemy.orm import DeclarativeBase, sessionmaker

# Создаем директорию для базы данных, если её нет
os.makedirs("db", exist_ok=True)

# Создаем подключение к базе данных
DATABASE_URL = "sqlite:///db/quiz_db.sqlite"
engine = create_engine(DATABASE_URL, echo=True)

# Создаем фабрику для сессий
SessionLocal = sessionmaker(bind=engine)


# Новый базовый класс для моделей
class Base(DeclarativeBase):
    pass


# Модель для таблицы вопросов
class Question(Base):
    __tablename__ = "questions"

    id = Column(Integer, primary_key=True, autoincrement=True)
    league = Column(String, nullable=False)  # Лига (Bronze, Silver, Gold)
    level = Column(String, nullable=False)  # Уровень сложности (Easy, Medium, Hard)
    question = Column(String, nullable=False)
    correct_answer = Column(String, nullable=False)
    answer_2 = Column(String, nullable=False)
    answer_3 = Column(String, nullable=False)
    answer_4 = Column(String, nullable=False)


class Users(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(BigInteger, nullable=False, unique=True)  # уникальное поле
    username = Column(String, nullable=True)
    league = Column(Integer, nullable=False, default=1)
    games = Column(Integer, nullable=False, default=0)
    balance_silver_coins = Column(Integer, nullable=False, default=500)
    balance_gold_coins = Column(Integer, nullable=False, default=0)
    balance_rub = Column(Integer, nullable=False, default=0)
    referrals = Column(Integer, nullable=False, default=0)


# Инициализация базы данных
Base.metadata.create_all(bind=engine)
