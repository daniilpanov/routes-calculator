# 20DC, 20HC, 40DC, 40HC
import enum
from sqlalchemy import String, Enum, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from src.database import Base


class ContainerType(enum.StrEnum):
    DC = 'DC'
    HC = 'HC'


class ContainerModel(Base):
    __tablename__ = 'containers'
    __table_args__ = (
        UniqueConstraint('size', 'type', 'weight_from', 'weight_to', 'name'),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    size: Mapped[int] = mapped_column()
    weight_from: Mapped[float] = mapped_column()
    weight_to: Mapped[float] = mapped_column()
    name: Mapped[str] = mapped_column(String(30))
    type: Mapped[ContainerType] = mapped_column(Enum(ContainerType, create_constraint=True, check_constraint=True, validate_strings=True))
