from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Text, func, Time
from sqlalchemy.orm import relationship
from passlib.hash import bcrypt
from datetime import datetime
from .database import Base

class User(Base):
    __tablename__ = 'user'
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(150), unique=True, nullable=False)
    email = Column(String(150), nullable=True)
    password_hash = Column(String(256), nullable=False)
    first_name = Column(String(150), nullable=False)
    second_name = Column(String(150), nullable=False)
    phone_hash = Column(String(256), unique=True, nullable=False)

    def set_password(self, password):
        self.password_hash = bcrypt.hash(password)

    def check_password(self, password):
        return bcrypt.verify(password, self.password_hash)

    def set_phone(self, phone):
        self.phone_hash = bcrypt.hash(phone)

    def check_phone(self, phone):
        return bcrypt.verify(phone, self.phone_hash)

class Location(Base):
    __tablename__ = 'location'
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(150), nullable=False)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    average_rating = Column(Float, default=0, nullable=False)
    rating_count = Column(Integer, default=0)
    created_by = Column(Integer, ForeignKey('user.id'), nullable=False)
    created_at = Column(DateTime, default=func.now())
    address = Column(String(255), nullable=True)
    working_hours_start = Column(Time, nullable=False)
    working_hours_end = Column(Time, nullable=False)
    average_check = Column(Integer, nullable=True)

    reviews = relationship('Review', backref='location')
    owner_info = relationship('OwnerInfo', backref='location', uselist=False)

class Review(Base):
    __tablename__ = 'review'
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('user.id'), nullable=False)
    location_id = Column(Integer, ForeignKey('location.id'), nullable=False)
    rating = Column(Integer, nullable=True)
    comment = Column(Text, nullable=True)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)

    user = relationship('User', backref='reviews')

class OwnerInfo(Base):
    __tablename__ = 'ownerinfo'
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('user.id'), nullable=False)
    location_id = Column(Integer, ForeignKey('location.id'), nullable=False)
    website = Column(String(200), nullable=True)
    owner_info = Column(Text, nullable=False)

    user = relationship('User', backref='owner_info')