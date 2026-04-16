from module_shared.database import Base
from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from . import RouteModel


class ServiceModel(Base):
    uid = ("name",)

    __tablename__ = "services"

    id: Mapped[int] = mapped_column(primary_key=True)  # noqa: A003
    name: Mapped[str] = mapped_column(String(150), unique=True, nullable=False)
    description: Mapped[str] = mapped_column(String(255), nullable=False)
    hint: Mapped[str | None] = mapped_column(String(255), nullable=True)


class ServicePriceModel(Base):
    uid = ("route_id", "service_id")

    __tablename__ = "service_prices"

    id: Mapped[int] = mapped_column(primary_key=True)  # noqa: A003

    route_id: Mapped[int] = mapped_column(
        ForeignKey(f"{RouteModel.__tablename__}.id", name="fk__service_prices_route"),
        nullable=False,
    )
    service_id: Mapped[int] = mapped_column(
        ForeignKey(f"{ServiceModel.__tablename__}.id", name="fk__service_prices_service"),
        nullable=False,
    )

    currency: Mapped[str] = mapped_column(String(10), nullable=False)
    price: Mapped[float] = mapped_column(nullable=False)

    route: Mapped[RouteModel] = relationship()
    service: Mapped[ServiceModel] = relationship()
