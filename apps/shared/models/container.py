import enum

from sqlalchemy import Enum, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from ..database import Base


class ContainerType(enum.Enum):
    DC = "DC"
    HC = "HC"


class ContainerModel(Base):
    uid = ("size", "type", "weight_from", "weight_to", "name")

    __tablename__ = "containers"
    __table_args__ = (UniqueConstraint(*uid),)

    id: Mapped[int] = mapped_column(primary_key=True)  # noqa: A003
    size: Mapped[int] = mapped_column()
    weight_from: Mapped[float] = mapped_column()
    weight_to: Mapped[float] = mapped_column()
    name: Mapped[str] = mapped_column(String(30))
    type: Mapped[ContainerType] = mapped_column(  # noqa: A003
        Enum(
            ContainerType,
            create_constraint=True,
            check_constraint=True,
            validate_strings=True,
        )
    )
