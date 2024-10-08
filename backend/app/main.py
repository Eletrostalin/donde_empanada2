from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import ValidationError
from sqlalchemy.ext.asyncio import AsyncSession

from .config import GOOGLE_MAPS_API_KEY
from .database import engine, Base
from .routes import auth, location


# Создаем все таблицы асинхронно
async def create_db_and_tables():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

# Инициализация FastAPI приложения
app = FastAPI()

# Настройка CORS (для взаимодействия с фронтендом)
origins = [
    "http://localhost:3000",  # Фронтенд будет работать на этом порту
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Роуты для аутентификации, работы с локациями и отзывами
app.include_router(auth.router)
app.include_router(location.router)

# Стартовая точка приложения
@app.on_event("startup")
async def on_startup():
    await create_db_and_tables()

@app.get("/")
async def root():
    return {"message": "Welcome to the FastAPI app!"}

@app.get("/google-maps-key")
def get_google_maps_key():
    return {"google_maps_api_key": GOOGLE_MAPS_API_KEY}

# Обработчик ошибок валидации
@app.exception_handler(ValidationError)
async def validation_exception_handler(request: Request, exc: ValidationError):
    # Форматируем ошибки для удобства пользователя
    errors = []
    for error in exc.errors():
        loc = " -> ".join([str(l) for l in error['loc']])
        msg = error['msg']
        errors.append(f"{loc}: {msg}")

    return JSONResponse(
        status_code=422,
        content={"detail": "Validation errors", "errors": errors}
    )
