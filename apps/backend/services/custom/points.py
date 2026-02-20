from functools import partial

from backend.mapper_decorator import apply_mapper
from shared.database import get_database
from shared.models import CompanyModel, PointModel, RouteModel
from sqlalchemy import select

from .mappers.points import map_point_ids, map_points


def _build_base_stmt():
    return select(PointModel).distinct()


def _build_stmt_joined_with_company_by_route(id_field):
    return (
        _build_base_stmt()
        .join(
            RouteModel,
            id_field == PointModel.id,
        )
        .join(CompanyModel)
        .add_columns(CompanyModel)
    )


def _build_stmt_fetch_all():
    return _build_stmt_joined_with_company_by_route(RouteModel.start_point_id).union(
        _build_stmt_joined_with_company_by_route(RouteModel.end_point_id),
    )


@apply_mapper(map_points)
async def get_all_points():
    async with get_database().session_context() as session:
        stmt = _build_stmt_fetch_all()
        response = await session.execute(stmt)

    return response.all()


@apply_mapper(map_point_ids)
async def get_points(*, id_field):
    async with get_database().session_context() as session:
        stmt = _build_base_stmt().join(RouteModel, id_field == PointModel.id)
        response = await session.execute(stmt)

    return response.scalars().all()


get_departure_points = partial(get_points, id_field=RouteModel.start_point_id)
get_destination_points = partial(get_points, id_field=RouteModel.end_point_id)
