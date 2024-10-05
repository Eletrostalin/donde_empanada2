import hashlib
import logging
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from jose import JWTError, jwt
from datetime import datetime, timedelta

from .. import models, schemas
from ..database import get_db

# Секретный ключ для подписи JWT
SECRET_KEY = "your_secret_key_here"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# Настраиваем логирование
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/auth",
    tags=["auth"]
)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")


# Функция для хэширования пароля с помощью hashlib (SHA-256)
def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()


# Функция для проверки пароля
def verify_password(plain_password: str, hashed_password: str) -> bool:
    return hash_password(plain_password) == hashed_password


# Функция для создания JWT токена
def create_access_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

# Регистрация пользователя
@router.post("/register")
async def register_user(user: schemas.RegistrationSchema, db: Session = Depends(get_db)):
    logger.info(f"Регистрация пользователя: {user.username}, email: {user.email}")
    stmt = select(models.User).where(models.User.username == user.username)
    result = await db.execute(stmt)
    db_user = result.scalar_one_or_none()
    if db_user:
        logger.warning(f"Пользователь {user.username} уже зарегистрирован")
        raise HTTPException(status_code=400, detail="Username already registered")

    hashed_password = hash_password(user.password)
    new_user = models.User(
        username=user.username,
        email=user.email,
        password_hash=hashed_password,
        first_name=user.first_name,
        second_name=user.second_name,
        phone_hash=hash_password(user.phone),  # Хэширование телефона
    )
    logger.info(f"Создан новый пользователь: {user.username}")
    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)
    return {"message": "User registered successfully"}

# Логин пользователя
@router.post("/login")
async def login_user(form_data: schemas.LoginSchema, db: Session = Depends(get_db)):
    logger.info(f"Попытка входа пользователя: {form_data.username}")
    stmt = select(models.User).where(models.User.username == form_data.username)
    result = await db.execute(stmt)
    user = result.scalar_one_or_none()

    if not user or not verify_password(form_data.password, user.password_hash):
        logger.warning(f"Неверное имя пользователя или пароль для {form_data.username}")
        raise HTTPException(status_code=400, detail="Incorrect username or password")

    # Генерация JWT токена
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    logger.info(f"Пользователь {form_data.username} успешно вошел в систему")
    return {"access_token": access_token, "token_type": "bearer"}

# Получение текущего пользователя
@router.get("/me")
async def get_current_user(db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    stmt = select(models.User).where(models.User.username == username)
    result = await db.execute(stmt)
    user = result.scalar_one_or_none()

    if user is None:
        raise credentials_exception

    logger.info(f"Текущий пользователь: {user.username}")
    return user