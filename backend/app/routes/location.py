from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from ..config import GOOGLE_MAPS_API_KEY
import logging  # Добавляем логирование

from .. import models, schemas
from ..database import get_db
from .auth import get_current_user

# Настройка логирования
logger = logging.getLogger(__name__)
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)
logger.addHandler(console_handler)
logger.setLevel(logging.INFO)

router = APIRouter(
    prefix="/locations",
    tags=["locations"]
)

# Создание новой локации с информацией о владельце (для зарегистрированных пользователей)
@router.post("/add-location", response_model=schemas.LocationSchema)
async def create_location_with_owner(
    location: schemas.LocationSchema,  # Схема для локации
    owner_info: schemas.OwnerInfoSchema = None,  # Схема для владельца (опционально)
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user)
):
    # Логирование полученных данных
    logger.info(f"Полученные данные локации: {location.dict()}")  # Если Pydantic модель
    if owner_info:
        logger.info(f"Полученные данные владельца: {owner_info.dict()}")

    logger.info(f"Попытка создания новой локации пользователем: {current_user.username}")

    # Создаем новую локацию
    new_location = models.Location(
        name=location.name,
        latitude=location.latitude,
        longitude=location.longitude,
        average_rating=0,
        rating_count=0,
        address=location.address,
        working_hours_start=location.working_hours_start,
        working_hours_end=location.working_hours_end,
        average_check=location.average_check,
        created_by=current_user.id
    )
    logger.info(f"Создана локация: {location.name}, пользователем: {current_user.username}")

    db.add(new_location)
    await db.commit()
    await db.refresh(new_location)  # Получаем обновленные данные локации

    # Если передана информация о владельце, создаем запись в таблице владельцев
    if owner_info:
        logger.info(f"Добавляем информацию о владельце для локации: {new_location.id}")
        new_owner_info = models.OwnerInfo(
            user_id=current_user.id,
            location_id=new_location.id,  # Привязываем к созданной локации
            website=owner_info.website,
            owner_info=owner_info.owner_info
        )
        db.add(new_owner_info)
        await db.commit()

    return new_location

# Получение списка всех локаций
@router.get("/", response_model=list[schemas.LocationSchema])
async def get_locations(db: AsyncSession = Depends(get_db)):
    logger.info("Получение списка всех локаций")
    stmt = select(models.Location)
    result = await db.execute(stmt)
    locations = result.scalars().all()
    return locations

# Получение конкретной локации по ID
@router.get("/{location_id}", response_model=schemas.LocationSchema)
async def get_location(location_id: int, db: AsyncSession = Depends(get_db)):
    logger.info(f"Получение локации с ID: {location_id}")
    stmt = select(models.Location).where(models.Location.id == location_id)
    result = await db.execute(stmt)
    location = result.scalar_one_or_none()
    if location is None:
        logger.warning(f"Локация с ID: {location_id} не найдена")
        raise HTTPException(status_code=404, detail="Location not found")
    return location