from sqlalchemy import String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

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
