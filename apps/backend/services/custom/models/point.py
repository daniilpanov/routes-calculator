import enum
from typing import Optional

from backend.database import Base
from sqlalchemy import Boolean, Enum, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship


class PointModel(Base):
    __tablename__ = "points"

    id: Mapped[int] = mapped_column(primary_key=True)  # noqa: A003
    parent_id: Mapped[int | None] = mapped_column(
        ForeignKey("points.id"), nullable=True
    )

    aliases: Mapped[list["PointAliasModel"]] = relationship(
        "PointAliasModel",
        back_populates="point",
        cascade="all, delete-orphan",
        lazy="selectin",
    )
    parent: Mapped[Optional["PointModel"]] = relationship(
        "PointModel",
        remote_side=[id],
    )


class LangType(enum.Enum):
    RU = "RU"
    EN = "EN"


class PointAliasModel(Base):
    __tablename__ = "aliases"

    id: Mapped[int] = mapped_column(primary_key=True)  # noqa: A003
    is_main: Mapped[bool] = mapped_column(Boolean, default=False)
    alias_name: Mapped[str] = mapped_column(String(25), nullable=False)

    point_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("points.id", ondelete="CASCADE")
    )
    point: Mapped[PointModel] = relationship(
        "PointModel",
        back_populates="aliases",
    )

    lang: Mapped[LangType] = mapped_column(
        Enum(
            LangType,
            create_constraint=True,
            check_constraint=True,
            validate_strings=True,
        )
    )
