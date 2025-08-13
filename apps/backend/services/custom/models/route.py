import datetime

from backend.database import Base
from sqlalchemy import DateTime, ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from . import CompanyModel, ContainerModel
from .point import PointModel


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
    company_id: Mapped[int] = mapped_column(ForeignKey("companies.id"))
    container_id: Mapped[int] = mapped_column(ForeignKey("containers.id"))
    start_point_id: Mapped[int] = mapped_column(ForeignKey("points.id"))
    end_point_id: Mapped[int] = mapped_column(ForeignKey("points.id"))
    effective_from: Mapped[datetime.date] = mapped_column(DateTime(timezone=False))
    effective_to: Mapped[datetime.date] = mapped_column(DateTime(timezone=False))

    fifo: Mapped[float | None] = mapped_column()
    filo: Mapped[float | None] = mapped_column()

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
    company_id: Mapped[int] = mapped_column(ForeignKey("companies.id"))
    container_id: Mapped[int] = mapped_column(ForeignKey("containers.id"))
    start_point_id: Mapped[int] = mapped_column(ForeignKey("points.id"))
    end_point_id: Mapped[int] = mapped_column(ForeignKey("points.id"))
    effective_from: Mapped[datetime.date] = mapped_column(DateTime(timezone=False))
    effective_to: Mapped[datetime.date] = mapped_column(DateTime(timezone=False))

    price: Mapped[float] = mapped_column()
    drop: Mapped[float] = mapped_column()
    guard: Mapped[float | None] = mapped_column()

    start_point: Mapped[PointModel] = relationship(
        PointModel, foreign_keys=[start_point_id]
    )
    end_point: Mapped[PointModel] = relationship(
        PointModel, foreign_keys=[end_point_id]
    )
    company: Mapped[CompanyModel] = relationship()
    container: Mapped[ContainerModel] = relationship()
