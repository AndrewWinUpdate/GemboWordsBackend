from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from typing import AsyncGenerator

from models import Base

# Создаем строку подключения к базе данных SQLite

# Для SQLite не требуется особая настройка подключения
# connect_args={"check_same_thread": False} нужно для работы с SQLite в многопоточной среде

engine = create_async_engine("postgresql+asyncpg://myuser:b38n4t34bitb3cb4tc3@localhost/gembowordsdb")



# Создаем фабрику сессий
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

async_session_maker = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

# Базовый класс для наших моделей


async def get_async_session() -> AsyncGenerator[AsyncSession, None]:
    async with async_session_maker() as session:
        yield session