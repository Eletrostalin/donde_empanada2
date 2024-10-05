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


# Создание новой локации с информацией о владельце (для зарегистрированных пользователей)
@router.post("/add-location", response_model=schemas.LocationSchema)
async def create_location_with_owner(
    location: schemas.LocationSchema,  # Схема для локации
    owner_info: schemas.OwnerInfoSchema = None,  # Схема для владельца (опционально)
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user)
):
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

    db.add(new_location)
    await db.commit()
    await db.refresh(new_location)  # Получаем обновленные данные локации

    # Если передана информация о владельце, создаем запись в таблице владельцев
    if owner_info:
        new_owner_info = models.OwnerInfo(
            user_id=current_user.id,
            location_id=new_location.id,  # Привязываем к созданной локации
            website=owner_info.website,
            owner_info=owner_info.owner_info
        )
        db.add(new_owner_info)
        await db.commit()

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



# Добавление информации о владельце
@router.post("/", response_model=schemas.OwnerInfoSchema)
async def create_owner_info(owner_info: schemas.OwnerInfoSchema, db: AsyncSession = Depends(get_db),
                            current_user=Depends(get_current_user)):
    # Проверяем, существует ли локация
    stmt = select(models.Location).where(models.Location.id == owner_info.location_id)
    result = await db.execute(stmt)
    location = result.scalar_one_or_none()

    if location is None:
        raise HTTPException(status_code=404, detail="Локация не найдена")

    # Проверяем, что пользователь является владельцем локации
    if location.created_by != current_user.id:
        raise HTTPException(status_code=403, detail="Недостаточно прав для добавления информации о владельце")

    # Добавляем информацию о владельце
    new_owner_info = models.OwnerInfo(
        user_id=current_user.id,
        location_id=owner_info.location_id,
        website=owner_info.website,
        owner_info=owner_info.owner_info
    )

    db.add(new_owner_info)
    await db.commit()
    await db.refresh(new_owner_info)

    return new_owner_info