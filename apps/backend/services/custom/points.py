import datetime
from functools import partial

from backend.database import database
from backend.mapper_decorator import apply_mapper
from sqlalchemy import select

from .mappers.points import map_points
from .models import CompanyModel, PointModel, RouteModel


def _build_stmt(date, id_field):
    return (  # noqa: ECE001
        select(
            PointModel,
            CompanyModel.name.label("company_name"),
        )
        .distinct()
        .join(
            RouteModel,
            (getattr(RouteModel, id_field) == PointModel.id)
            & (RouteModel.effective_from <= date)
            & (RouteModel.effective_to >= date),
        )
        .join(CompanyModel)
    )


@apply_mapper(map_points)
async def get_points(date: datetime.date, _=None, *, id_field):
    async with database.session() as session:
        stmt = _build_stmt(date, id_field)
        response = await session.execute(stmt)

    return response.all()


get_departure_points_by_date = partial(get_points, id_field="start_point_id")
get_destination_points_by_date = partial(get_points, id_field="end_point_id")
