from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from src.database import Base


class СurrencyModel(Base):

    __tablename__ = "currencies"

    id: Mapped[int] = mapped_column(primary_key=True)  # noqa: A003
    currency_name: Mapped[str] = mapped_column(String(30), unique=True)
