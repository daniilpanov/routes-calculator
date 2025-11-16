import asyncio
import datetime

from backend.database import database
from backend.mapper_decorator import apply_mapper
from sqlalchemy import select
from sqlalchemy.orm import aliased, joinedload

from .mappers.routes import map_routes
from .models import RailRouteModel, SeaRouteModel


async def _execute_query(q):
    async with database.session() as session:
        result = await session.execute(q)
    return result.all()


@apply_mapper(map_routes)
async def find_all_paths(
    date: datetime.date,
    start_point_id: int,
    end_point_id: int,
    container_ids: list[int],
) -> list[dict]:
    sea = aliased(SeaRouteModel)
    rail = aliased(RailRouteModel)
    rail2 = aliased(RailRouteModel)

    query_rail = (  # noqa: ECE001
        select(rail)
        .where(
            (rail.effective_from <= date)
            & (rail.effective_to >= date)
            & (rail.start_point_id == start_point_id)
            & (rail.end_point_id == end_point_id)
            & rail.container_id.in_(container_ids)
        )
        .options(
            joinedload(rail.start_point),
            joinedload(rail.end_point),
            joinedload(rail.company),
            joinedload(rail.container),
        )
    )
    query_sea = (  # noqa: ECE001
        select(sea)
        .where(
            (sea.effective_from <= date)
            & (sea.effective_to >= date)
            & (sea.start_point_id == start_point_id)
            & (sea.end_point_id == end_point_id)
            & sea.container_id.in_(container_ids)
        )
        .options(
            joinedload(sea.start_point),
            joinedload(sea.end_point),
            joinedload(sea.company),
            joinedload(sea.container),
        )
    )
    query_sea_rail = (  # noqa: ECE001
        select(sea, rail)
        .where(
            (sea.effective_from <= date)
            & (sea.effective_to >= date)
            & (rail.effective_from <= date)
            & (rail.effective_to >= date)
            & (sea.start_point_id == start_point_id)
            & (rail.end_point_id == end_point_id)
            & sea.container_id.in_(container_ids)
        )
        .join(
            rail,
            (sea.end_point_id == rail.start_point_id)
            & (sea.container_id == rail.container_id),
        )
        .options(
            joinedload(sea.start_point),
            joinedload(sea.end_point),
            joinedload(sea.company),
            joinedload(sea.container),
            joinedload(rail.start_point),
            joinedload(rail.end_point),
            joinedload(rail.company),
            joinedload(rail.container),
        )
    )

    all_queries = [
        query_rail,
        query_sea,
        query_sea_rail,
    ]

    coroutines = [_execute_query(query) for query in all_queries]
    results = await asyncio.gather(*coroutines, return_exceptions=True)
    flat_result: list[dict] = []

    for r in results:
        if r and not isinstance(r, BaseException):
            flat_result.extend(r)

    return flat_result
