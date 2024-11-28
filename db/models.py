from sqlalchemy import Column, Integer, String, create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker


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


# Создаем подключение к базе данных
DATABASE_URL = "sqlite:///quiz_db.sqlite"
engine = create_engine(DATABASE_URL, echo=True)

# Создаем фабрику для сессий
SessionLocal = sessionmaker(bind=engine)

# Инициализация базы данных
Base.metadata.create_all(bind=engine)
