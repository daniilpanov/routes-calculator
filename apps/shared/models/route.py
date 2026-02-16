import datetime
import enum

from sqlalchemy import DateTime, Enum, ForeignKey, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..database import Base
from . import CompanyModel, ContainerModel
from .point import PointModel


class RouteTypeEnum(enum.Enum):
    SEA = "sea"
    RAIL = "rail"
    SEA_RAIL = "sea_rail"


class PriceTypeEnum(enum.Enum):
    FIFOR = "FIFO"
    FILO = "FILO"
    FOBFOR = "FOR"
    MIXED = "MIXED"


class PriceModel(Base):
    uid = (
        "route_id",
        "container_id",
        "type",
    )

    __tablename__ = "prices"
    __table_args__ = (UniqueConstraint(*uid),)

    id: Mapped[int] = mapped_column(primary_key=True)  # noqa: A003

    route_id: Mapped[int] = mapped_column(ForeignKey("routes.id"))
    container_id: Mapped[int] = mapped_column(ForeignKey("containers.id"))

    value: Mapped[float | None] = mapped_column(nullable=True, default=None)
    currency: Mapped[str] = mapped_column(String(10))
    conversation_percents: Mapped[float] = mapped_column(default=0)

    type: Mapped[PriceTypeEnum] = mapped_column(  # noqa: A003
        Enum(
            PriceTypeEnum,
            create_constraint=True,
            check_constraint=True,
            validate_strings=True,
        )
    )

    container: Mapped[ContainerModel] = relationship()
    route: Mapped['RouteModel'] = relationship("RouteModel", back_populates="prices")


class RouteModel(Base):
    uid = (
        "company_id",
        "start_point_id",
        "end_point_id",
        "effective_from",
        "effective_to",
    )

    __tablename__ = "routes"
    __table_args__ = (UniqueConstraint(*uid),)

    id: Mapped[int] = mapped_column(primary_key=True)  # noqa: A003

    company_id: Mapped[int] = mapped_column(ForeignKey("companies.id"))
    start_point_id: Mapped[int] = mapped_column(ForeignKey("points.id"))
    end_point_id: Mapped[int] = mapped_column(ForeignKey("points.id"))

    effective_from: Mapped[datetime.date] = mapped_column(DateTime(timezone=False))
    effective_to: Mapped[datetime.date] = mapped_column(DateTime(timezone=False))
    comment: Mapped[str | None] = mapped_column(String(255), nullable=True, default=None)

    type: Mapped[RouteTypeEnum] = mapped_column(  # noqa: A003
        Enum(
            RouteTypeEnum,
            create_constraint=True,
            check_constraint=True,
            validate_strings=True,
        )
    )

    start_point: Mapped[PointModel] = relationship(
        PointModel, foreign_keys=[start_point_id]
    )
    end_point: Mapped[PointModel] = relationship(
        PointModel, foreign_keys=[end_point_id]
    )
    company: Mapped[CompanyModel] = relationship()
    prices: Mapped[list[PriceModel]] = relationship("PriceModel", back_populates="route")
