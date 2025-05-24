# CompanyID: ..., ContainerID: ..., PointID: ..., Price: <number>, PriceType: <simple/fifo/filo>; etc.
from sqlalchemy import ForeignKey, Enum, PrimaryKeyConstraint
from sqlalchemy.orm import Mapped, mapped_column

from src.database import Base


class PriceType(str, Enum):
    SIMPLE = 'simple'
    FIFO = 'fifo'
    FILO = 'filo'


class PriceModel(Base):
    __tablename__ = 'prices'
    __table_args__ = (
        PrimaryKeyConstraint('route_id', 'container_id', 'price_type'),
    )

    route_id: Mapped[int] = mapped_column(ForeignKey('routes.id'))
    container_id: Mapped[int] = mapped_column(ForeignKey('containers.id'))
    price: Mapped[float] = mapped_column()
    price_type: Mapped[PriceType] = mapped_column()
