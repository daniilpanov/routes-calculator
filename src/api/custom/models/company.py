# HUB SERVICE
from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from src.database import Base


class CompanyModel(Base):
    __tablename__ = 'companies'

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(30), unique=True)
