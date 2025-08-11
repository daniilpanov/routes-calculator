import datetime
from typing import List, Optional

from sqlalchemy import DateTime, ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.database import Base
from . import CompanyModel, ContainerModel
from .point import PointModel
from .price import RoutePriceModel


class RouteModel(Base):
    uid = (
        "company_id",
        "container_id",
        "start_point_id",
        "end_point_id",
        "effective_from",
        "effective_to",
    )
    __tablename__ = "routes"
    __table_args__ = (UniqueConstraint(*uid),)

    id: Mapped[int] = mapped_column(primary_key=True)  # noqa: A003
    company_id: Mapped[int] = mapped_column(ForeignKey("companies.id"))
    container_id: Mapped[int] = mapped_column(ForeignKey("containers.id"))
    start_point_id: Mapped[int] = mapped_column(ForeignKey("points.id"))
    end_point_id: Mapped[int] = mapped_column(ForeignKey("points.id"))
    effective_from: Mapped[datetime.date] = mapped_column(DateTime(timezone=False))
    effective_to: Mapped[datetime.date] = mapped_column(DateTime(timezone=False))

    start_point: Mapped[PointModel] = relationship(
        PointModel, foreign_keys=[start_point_id]
    )
    end_point: Mapped[PointModel] = relationship(
        PointModel, foreign_keys=[end_point_id]
    )
    company: Mapped[CompanyModel] = relationship()
    container: Mapped[ContainerModel] = relationship()

    prices: Mapped[List["RoutePriceModel"]] = relationship("RoutePriceModel", backref="route")

    @property
    def price(self) -> Optional[int]:
        if self.prices:
            return self.prices[0].value
        return None
