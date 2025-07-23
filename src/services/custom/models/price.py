from sqlalchemy import ForeignKey, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.database import Base


class СurrencyModel(Base):

    __tablename__ = "currencies"

    id: Mapped[int] = mapped_column(primary_key=True)  # noqa: A003
    currency_name: Mapped[str] = mapped_column(String(30), unique=True)


class PriceTypeModel(Base):
    uid = ("name",)

    __tablename__ = "price_types"
    __table_args__ = (UniqueConstraint(*uid),)

    id: Mapped[int] = mapped_column(primary_key=True)  # noqa: A003
    name: Mapped[str] = mapped_column(String(30))
    need_drop: Mapped[bool] = mapped_column()
    direction: Mapped[int] = mapped_column()


class RoutePriceModel(Base):

    __tablename__ = "routes_prices"

    id: Mapped[int] = mapped_column(primary_key=True)  # noqa: A003
    route_id: Mapped[int] = mapped_column(ForeignKey("routes.id"))
    price_type_id: Mapped[int] = mapped_column(ForeignKey("price_types.id"))
    currency_id: Mapped[int] = mapped_column(ForeignKey("currencies.id"))
    value: Mapped[int] = mapped_column()
    conversation_percent: Mapped[int] = mapped_column()

    price_type: Mapped["PriceTypeModel"] = relationship("PriceTypeModel")
