from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from models import Base

# Создаем строку подключения к базе данных SQLite
SQLALCHEMY_DATABASE_URL = "sqlite:///./database.db"

# Для SQLite не требуется особая настройка подключения
# connect_args={"check_same_thread": False} нужно для работы с SQLite в многопоточной среде
engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)

# Создаем фабрику сессий
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Базовый класс для наших моделей


# Функция для получения сессии базы данных
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
