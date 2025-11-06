from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    name = Column(String, nullable=True)

    # Profile fields useful for TDEE/BMR
    age = Column(Integer, nullable=True)
    sex = Column(String(10), nullable=True)           # "male" | "female"
    height_cm = Column(Float, nullable=True)
    weight_kg = Column(Float, nullable=True)
    activity_level = Column(String(20), nullable=True) # "sedentary", "light", "moderate", "active", "athlete"
    goal = Column(String(20), nullable=True)           # "cut" | "maintain" | "bulk"

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    is_verified = Column(Boolean, nullable=False, server_default="false")
    password_changed_at = Column(DateTime(timezone=True), nullable=True)

    sessions = relationship(
        "Session",
        back_populates="user",
        cascade="all, delete-orphan",
    )