import datetime
from functools import partial

from sqlalchemy import select

from src.database import database
from src.mapper_decorator import apply_mapper
from .mappers.points import map_points
from .models import CompanyModel, PointModel, RouteModel


def _build_stmt(date: datetime.date, id_field: str):
    route_col = getattr(RouteModel, id_field)

    cond_point_match = route_col == PointModel.id
    cond_valid_from = RouteModel.effective_from <= date
    cond_valid_to = RouteModel.effective_to >= date

    # Упростим выражение по шагам
    join_cond_1 = cond_point_match & cond_valid_from
    join_condition = join_cond_1 & cond_valid_to

    return (  # noqa: ECE001
        select(
            PointModel,
            CompanyModel.name.label("company_name"),
        )
        .distinct()
        .join(RouteModel, join_condition)
        .join(CompanyModel, CompanyModel.id == RouteModel.company_id)
    )


@apply_mapper(map_points)
async def get_points(date: datetime.date, _=None, *, id_field: str):
    async with database.session() as session:
        stmt = _build_stmt(date, id_field)
        result = await session.execute(stmt)
    return result.all()


get_departure_points_by_date = partial(get_points, id_field="start_point_id")
get_destination_points_by_date = partial(get_points, id_field="end_point_id")
