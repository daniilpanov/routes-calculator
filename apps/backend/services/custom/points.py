import datetime
from functools import partial

from backend.database import database
from backend.mapper_decorator import apply_mapper
from sqlalchemy import select
from sqlalchemy.orm import aliased

from .mappers.points import map_points
from .models import CompanyModel, PointModel, RailRouteModel, SeaRouteModel


def _build_stmt(date, route_class, id_field):
    pointCountry = aliased(PointModel)
    return (  # noqa: ECE001
        select(
            PointModel,
            CompanyModel.name.label("company_name"),
            pointCountry.name.label("country"),
        )
        .distinct()
        .join(
            route_class,
            (getattr(route_class, id_field) == PointModel.id)
            & (route_class.effective_from <= date)
            & (route_class.effective_to >= date),
        )
        .join(CompanyModel)
        .join(
            pointCountry,
            (PointModel.parent_id == pointCountry.id)
            & (pointCountry.parent_id.is_(None)),
        )
    )


@apply_mapper(map_points)
async def get_points(date: datetime.date, _=None, *, id_field):
    async with database.session() as session:
        stmt_from_rail = _build_stmt(date, RailRouteModel, id_field)
        stmt_from_sea = _build_stmt(date, SeaRouteModel, id_field)

        stmt = stmt_from_rail.union(stmt_from_sea)
        result = await session.execute(stmt)

    return result.all()


get_departure_points_by_date = partial(get_points, id_field="start_point_id")
get_destination_points_by_date = partial(get_points, id_field="end_point_id")
