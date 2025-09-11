import datetime

from sqlalchemy import DateTime, ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..database import Base
from . import CompanyModel, ContainerModel
from .point import PointModel


class BatchModel(Base):
    __tablename__ = "batches"
    id: Mapped[int] = mapped_column(primary_key=True)  # noqa: A003
    create_date: Mapped[datetime.date] = mapped_column(DateTime(timezone=False))


class SeaRouteModel(Base):
    uid = (
        "company_id",
        "container_id",
        "start_point_id",
        "end_point_id",
        "effective_from",
        "effective_to",
    )

    __tablename__ = "sea_routes"
    __table_args__ = (UniqueConstraint(*uid),)

    id: Mapped[int] = mapped_column(primary_key=True)  # noqa: A003
    batch_id: Mapped[int | None] = mapped_column(ForeignKey("batches.id"))
    company_id: Mapped[int] = mapped_column(ForeignKey("companies.id"))
    container_id: Mapped[int] = mapped_column(ForeignKey("containers.id"))
    start_point_id: Mapped[int] = mapped_column(ForeignKey("points.id"))
    end_point_id: Mapped[int] = mapped_column(ForeignKey("points.id"))
    effective_from: Mapped[datetime.date] = mapped_column(DateTime(timezone=False))
    effective_to: Mapped[datetime.date] = mapped_column(DateTime(timezone=False))

    fifo: Mapped[float | None] = mapped_column(nullable=True)
    filo: Mapped[float | None] = mapped_column(nullable=True)

    start_point: Mapped[PointModel] = relationship(
        PointModel, foreign_keys=[start_point_id]
    )
    end_point: Mapped[PointModel] = relationship(
        PointModel, foreign_keys=[end_point_id]
    )
    company: Mapped[CompanyModel] = relationship()
    container: Mapped[ContainerModel] = relationship()

    @property
    def price(self):
        return self.filo or self.fifo


class RailRouteModel(Base):
    uid = (
        "company_id",
        "container_id",
        "start_point_id",
        "end_point_id",
        "effective_from",
        "effective_to",
    )

    __tablename__ = "rail_routes"
    __table_args__ = (UniqueConstraint(*uid),)

    id: Mapped[int] = mapped_column(primary_key=True)  # noqa: A003
    batch_id: Mapped[int | None] = mapped_column(ForeignKey("batches.id"))
    company_id: Mapped[int] = mapped_column(ForeignKey("companies.id"))
    container_id: Mapped[int] = mapped_column(ForeignKey("containers.id"))
    start_point_id: Mapped[int] = mapped_column(ForeignKey("points.id"))
    end_point_id: Mapped[int] = mapped_column(ForeignKey("points.id"))
    effective_from: Mapped[datetime.date] = mapped_column(DateTime(timezone=False))
    effective_to: Mapped[datetime.date] = mapped_column(DateTime(timezone=False))

    price: Mapped[float] = mapped_column()
    drop: Mapped[float] = mapped_column()
    guard: Mapped[float | None] = mapped_column(nullable=True, default=None)

    start_point: Mapped[PointModel] = relationship(
        PointModel, foreign_keys=[start_point_id]
    )
    end_point: Mapped[PointModel] = relationship(
        PointModel, foreign_keys=[end_point_id]
    )
    company: Mapped[CompanyModel] = relationship()
    container: Mapped[ContainerModel] = relationship()
