import datetime
from functools import partial

from sqlalchemy import select
from sqlalchemy.orm import aliased

from src.database import database
from src.mapper_decorator import apply_mapper
from .mappers.points import map_points
from .models import CompanyModel, PointModel, RailRouteModel, SeaRouteModel
from .models.point import LangType, PointAliasModel


def _build_stmt(date, route_class, id_field):
    RuAlias = aliased(PointAliasModel)
    EnAlias = aliased(PointAliasModel)

    return (  # noqa: ECE001
        select(
            PointModel,
            CompanyModel.name.label("company_name"),
            EnAlias.alias_name.label("city"),
            RuAlias.alias_name.label("RU_city"),
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
            EnAlias,
            (EnAlias.point_id == PointModel.id)
            & (EnAlias.lang == LangType.EN)
            & (EnAlias.is_main == 1),
        )
        .join(
            RuAlias,
            (RuAlias.point_id == PointModel.id)
            & (RuAlias.lang == LangType.RU)
            & (RuAlias.is_main == 1),
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
