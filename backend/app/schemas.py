from datetime import datetime

from pydantic import BaseModel, EmailStr, Field, root_validator, model_validator
from typing import Optional

# Модель регистрации
class RegistrationSchema(BaseModel):
    username: str = Field(..., max_length=150, pattern='^[a-zA-Z]+$')
    email: Optional[EmailStr]
    password: str = Field(..., min_length=8)
    confirm_password: str = Field(..., min_length=8)
    first_name: str = Field(..., max_length=150, pattern='^[a-zA-Z]+$')
    second_name: str = Field(..., max_length=150, pattern='^[a-zA-Z]+$')
    phone: str = Field(..., pattern='^[0-9]+$')

    @model_validator(mode='after')
    def check_passwords_match(cls, values):
        password = values.password
        confirm_password = values.confirm_password
        if password != confirm_password:
            raise ValueError('Пароли не совпадают')
        if not any(char.isdigit() for char in password) or not any(char.islower() for char in password):
            raise ValueError('Пароль должен содержать хотя бы одну цифру и одну строчную букву')
        return values

# Модель для логина пользователя
class LoginSchema(BaseModel):
    username: str
    password: str

# Модель для локаций
class LocationSchema(BaseModel):
    name: str = Field(..., max_length=150)
    latitude: float = Field(..., description="Широта для карты", example=55.7558)
    longitude: float = Field(..., description="Долгота для карты", example=37.6173)
    average_rating: float = Field(0, ge=0, le=5, description="Средний рейтинг, рассчитывается автоматически", example=0)
    rating_count: int = Field(0, ge=0, description="Количество оценок", example=0)
    address: Optional[str] = Field(None, max_length=255)
    working_hours_start: str = Field(..., description="Начало рабочего времени", example="09:00")
    working_hours_end: str = Field(..., description="Конец рабочего времени", example="21:00")
    average_check: Optional[int] = Field(None, ge=2000, le=5000, description="Средний чек, если известен", example=3000)
    created_by: int = Field(..., description="ID пользователя, создавшего локацию")
    created_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        orm_mode = True

# Модель для отзывов
class ReviewSchema(BaseModel):
    rating: int = Field(..., ge=1, le=5)
    comment: str