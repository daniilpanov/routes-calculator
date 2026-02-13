from functools import partial

from backend.mapper_decorator import apply_mapper
from shared.database import get_database
from shared.models import CompanyModel, PointModel, RouteModel
from sqlalchemy import select

from .mappers.points import map_points


def _build_stmt(id_field):
    return (  # noqa: ECE001
        select(
            PointModel,
            CompanyModel.name.label("company_name"),
        )
        .distinct()
        .join(
            RouteModel,
            getattr(RouteModel, id_field) == PointModel.id,
        )
        .join(CompanyModel)
    )


@apply_mapper(map_points)
async def get_points(*, id_field):
    async with get_database().session_context() as session:
        stmt = _build_stmt(id_field)
        response = await session.execute(stmt)

    return response.all()


get_departure_points = partial(get_points, id_field="start_point_id")
get_destination_points = partial(get_points, id_field="end_point_id")
