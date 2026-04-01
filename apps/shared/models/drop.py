import datetime

from sqlalchemy import DateTime, ForeignKey, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..database import Base
from . import CompanyModel, ContainerModel
from .point import PointModel


class DropModel(Base):
    uid = (
        "sea_start_point_id",
        "sea_end_point_id",
        "rail_start_point_id",
        "rail_end_point_id",
        "container_id",
        "company_id",
        "effective_from",
        "effective_to",
    )

    __tablename__ = "drop"
    __table_args__ = (UniqueConstraint(*uid, name="uk__fingerprint"),)

    id: Mapped[int] = mapped_column(primary_key=True)  # noqa: A003

    company_id: Mapped[int] = mapped_column(ForeignKey("companies.id", name="fk__drop_companies"))
    container_id: Mapped[int] = mapped_column(ForeignKey("containers.id", name="fk__drop_container"))
    sea_start_point_id: Mapped[int | None] = mapped_column(
        ForeignKey("points.id", name="fk__drop_point__sea_start"),
        nullable=True,
    )
    sea_end_point_id: Mapped[int | None] = mapped_column(
        ForeignKey("points.id", name="fk__drop_point__sea_end"),
        nullable=True,
    )
    rail_start_point_id: Mapped[int | None] = mapped_column(
        ForeignKey("points.id", name="fk__drop_point__rail_start"),
        nullable=True,
    )
    rail_end_point_id: Mapped[int | None] = mapped_column(
        ForeignKey("points.id", name="fk__drop_point__rail_end"),
        nullable=True,
    )

    effective_from: Mapped[datetime.date] = mapped_column(DateTime(timezone=False))
    effective_to: Mapped[datetime.date] = mapped_column(DateTime(timezone=False))
    price: Mapped[float] = mapped_column(default=0)
    conversation_percents: Mapped[float] = mapped_column(default=0)
    currency: Mapped[str] = mapped_column(String(25))

    sea_start_point: Mapped[PointModel | None] = relationship(
        PointModel, foreign_keys=[sea_start_point_id]
    )
    sea_end_point: Mapped[PointModel | None] = relationship(
        PointModel, foreign_keys=[sea_end_point_id]
    )
    rail_start_point: Mapped[PointModel | None] = relationship(
        PointModel, foreign_keys=[rail_start_point_id]
    )
    rail_end_point: Mapped[PointModel | None] = relationship(
        PointModel, foreign_keys=[rail_end_point_id]
    )
    company: Mapped[CompanyModel] = relationship()
    container: Mapped[ContainerModel] = relationship()
