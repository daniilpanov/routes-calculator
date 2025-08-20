from typing import Optional

from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.database import Base


class PointModel(Base):
    __tablename__ = "points"

    id: Mapped[int] = mapped_column(primary_key=True)  # noqa: A003
    name: Mapped[str] = mapped_column(String(25))
    parent_id: Mapped[int | None] = mapped_column(
        ForeignKey("points.id"), nullable=True
    )

    parent: Mapped[Optional["PointModel"]] = relationship(
        "PointModel",
        remote_side=[id],
    )
