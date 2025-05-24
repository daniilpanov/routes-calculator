# City: St. Petersburg, Country: Russia, Type: Train, RU_City: Санкт-Петербург, RU_Country: Россия; etc.
import enum
from sqlalchemy import String, Enum, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from src.database import Base


class PointType(enum.StrEnum):
    TRAIN = 'train'
    SEA = 'sea'
    TRUCK = 'truck'


class PointModel(Base):
    __tablename__ = 'points'
    __table_args__ = (
        UniqueConstraint('city', 'country', 'type'),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    city: Mapped[str] = mapped_column(String(100))
    country: Mapped[str] = mapped_column(String(50))
    type: Mapped[PointType] = mapped_column(Enum(PointType, create_constraint=True, check_constraint=True, validate_strings=True))
    RU_city: Mapped[str] = mapped_column(String(100))
    RU_country: Mapped[str] = mapped_column(String(50))
