# CompanyID: ..., ContainerID: ..., PointID: ..., Price: <number>, PriceType: <simple/fifo/filo>; etc.
from sqlalchemy import ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from src.database import Base


class RouteModel(Base):
    __tablename__ = 'routes'
    __table_args__ = (
        UniqueConstraint('company_id', 'container_id', 'start_point_id', 'end_point_id'),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    company_id: Mapped[int] = mapped_column(ForeignKey('companies.id'))
    container_id: Mapped[int] = mapped_column(ForeignKey('containers.id'))
    start_point_id: Mapped[int] = mapped_column(ForeignKey('points.id'))
    end_point_id: Mapped[int] = mapped_column(ForeignKey('points.id'))
