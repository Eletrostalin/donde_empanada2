from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from .config import DATABASE_URL

# Создаем асинхронный движок для работы с базой данных
engine = create_async_engine(DATABASE_URL, echo=True, future=True)

# Создаем асинхронную сессию
async_session = sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False)

Base = declarative_base()

# Асинхронная функция для получения сессии
async def get_db():
    async with async_session() as session:
        yield session