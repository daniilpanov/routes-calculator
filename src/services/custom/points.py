import datetime
from functools import partial

from sqlalchemy import select

from src.database import database
from src.mapper_decorator import apply_mapper
from .mappers.points import map_points
from .models import PointModel, SeaRouteModel, RailRouteModel


@apply_mapper(map_points)
async def get_points(date: datetime.date, _=None, *, _id_field):
    async with database.session() as session:
        stmt = (
            select(PointModel)
            .where(
                PointModel.id.in_(select(getattr(SeaRouteModel, _id_field)).distinct().where(
                    (SeaRouteModel.effective_from <= date)
                    & (SeaRouteModel.effective_to >= date)
                )) | PointModel.id.in_(select(getattr(RailRouteModel, _id_field)).distinct().where(
                    (RailRouteModel.effective_from <= date)
                    & (RailRouteModel.effective_to >= date)
                ))
            )
        )
        result = await session.execute(stmt)
    return result.scalars().all()


get_departure_points_by_date = partial(get_points, _id_field='start_point_id')
get_destination_points_by_date = partial(get_points, _id_field='end_point_id')
