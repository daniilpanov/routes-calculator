# City: St. Petersburg, Country: Russia, Type: Train, RU_City: Санкт-Петербург, RU_Country: Россия; etc.
from sqlalchemy import String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column
from typing_extensions import Optional

from src.database import Base



class PointModel(Base):
    uid = ('city', 'country')

    __tablename__ = 'points'
    __table_args__ = (
        UniqueConstraint(*uid),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    city: Mapped[str] = mapped_column(String(100))
    country: Mapped[str] = mapped_column(String(50))
    RU_city: Mapped[Optional[str]] = mapped_column(String(100))
    RU_country: Mapped[Optional[str]] = mapped_column(String(50))
