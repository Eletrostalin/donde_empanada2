from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from ..config import GOOGLE_MAPS_API_KEY

from .. import models, schemas
from ..database import get_db
from .auth import get_current_user

router = APIRouter(
    prefix="/locations",
    tags=["locations"]
)


# Создание новой локации (только для зарегистрированных пользователей)
@router.post("/add-location", response_model=schemas.LocationSchema)
async def create_location(location: schemas.LocationSchema, db: AsyncSession = Depends(get_db),
                          current_user=Depends(get_current_user)):
    # Создаем новую локацию с нуля, указывая необходимые значения
    new_location = models.Location(
        name=location.name,
        latitude=location.latitude,  # Широта передается с фронта
        longitude=location.longitude,  # Долгота передается с фронта
        average_rating=0,  # Средний рейтинг по умолчанию 0
        rating_count=0,  # Количество оценок по умолчанию 0
        address=location.address,  # Адрес заполняется пользователем (опционально)
        working_hours_start=location.working_hours_start,  # Время начала работы
        working_hours_end=location.working_hours_end,  # Время окончания работы
        average_check=location.average_check,  # Средний чек (опционально)
        created_by=current_user.id  # ID пользователя берется автоматически из current_user
    )

    # Добавляем новую локацию в сессию и сохраняем в базе данных
    db.add(new_location)
    await db.commit()
    await db.refresh(new_location)  # Обновляем объект, чтобы получить все поля (например, id)

    # Возвращаем созданную локацию
    return new_location


# Получение списка всех локаций (публичный маршрут)
@router.get("/", response_model=list[schemas.LocationSchema])
async def get_locations(db: AsyncSession = Depends(get_db)):
    stmt = select(models.Location)
    result = await db.execute(stmt)
    locations = result.scalars().all()
    return locations


# Получение конкретной локации по ID (публичный маршрут)
@router.get("/{location_id}", response_model=schemas.LocationSchema)
async def get_location(location_id: int, db: AsyncSession = Depends(get_db)):
    stmt = select(models.Location).where(models.Location.id == location_id)
    result = await db.execute(stmt)
    location = result.scalar_one_or_none()
    if location is None:
        raise HTTPException(status_code=404, detail="Location not found")
    return location


# Обновление информации о локации (для всех зарегистрированных пользователей)
@router.put("/{location_id}", response_model=schemas.LocationSchema)
async def update_location(location_id: int, location_data: schemas.LocationSchema, db: AsyncSession = Depends(get_db),
                          current_user=Depends(get_current_user)):
    stmt = select(models.Location).where(models.Location.id == location_id)
    result = await db.execute(stmt)
    location = result.scalar_one_or_none()

    if location is None:
        raise HTTPException(status_code=404, detail="Location not found")

    # Обновляем информацию о локации
    location.name = location_data.name
    location.address = location_data.address
    location.working_hours_start = location_data.working_hours_start
    location.working_hours_end = location_data.working_hours_end
    location.average_check = location_data.average_check

    await db.commit()
    await db.refresh(location)
    return location


# Удаление локации (только для администраторов, сейчас объявим функцию с pass)
@router.delete("/{location_id}")
async def delete_location(location_id: int, db: AsyncSession = Depends(get_db), current_user=Depends(get_current_user)):
    # Проверка роли администратора
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Not enough permissions")

    stmt = select(models.Location).where(models.Location.id == location_id)
    result = await db.execute(stmt)
    location = result.scalar_one_or_none()

    if location is None:
        raise HTTPException(status_code=404, detail="Location not found")

    # Пока реализуем как pass, позже добавим удаление
    pass


