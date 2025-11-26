import asyncio
import datetime

from backend.database import database
from backend.mapper_decorator import apply_mapper
from sqlalchemy import select
from sqlalchemy.orm import aliased, joinedload

from .mappers.routes import map_routes
from .models import DropModel, RailRouteModel, SeaRouteModel


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
    drop = aliased(DropModel)

    query_rail = (  # noqa: ECE001
        select(rail, drop)
        .where(
            (rail.effective_from <= date)
            & (rail.effective_to >= date)
            & (rail.start_point_id == start_point_id)
            & (rail.end_point_id == end_point_id)
            & rail.container_id.in_(container_ids)
        )
        .outerjoin(
            drop,
            (rail.start_point_id == drop.rail_start_point_id)
            & (rail.end_point_id == drop.rail_end_point_id)
            & (rail.company_id == drop.company_id)
            & (rail.container_id == drop.container_id)
            & (drop.sea_start_point_id == None)  # noqa: E711
            & (drop.sea_end_point_id == None),  # noqa: E711
        )
        .options(
            joinedload(rail.start_point),
            joinedload(rail.end_point),
            joinedload(rail.company),
            joinedload(rail.container),
        )
    )
    query_sea = (  # noqa: ECE001
        select(sea, drop)
        .where(
            (sea.effective_from <= date)
            & (sea.effective_to >= date)
            & (sea.start_point_id == start_point_id)
            & (sea.end_point_id == end_point_id)
            & sea.container_id.in_(container_ids)
        )
        .outerjoin(
            drop,
            (drop.rail_start_point_id == None)  # noqa: E711
            & (drop.rail_end_point_id == None)  # noqa: E711
            & (sea.start_point_id == drop.sea_start_point_id)
            & (sea.end_point_id == drop.sea_end_point_id)
            & (sea.company_id == drop.company_id)
            & (sea.container_id == drop.container_id),
        )
        .options(
            joinedload(sea.start_point),
            joinedload(sea.end_point),
            joinedload(sea.company),
            joinedload(sea.container),
        )
    )
    query_sea_rail = (  # noqa: ECE001
        select(sea, rail, drop)
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
        .outerjoin(
            drop,
            (rail.start_point_id == drop.rail_start_point_id)
            & (rail.end_point_id == drop.rail_end_point_id)
            & (rail.company_id == drop.company_id)
            & (rail.container_id == drop.container_id)
            & (sea.start_point_id == drop.sea_start_point_id)
            & (sea.end_point_id == drop.sea_end_point_id)
            & (sea.company_id == drop.company_id)
            & (sea.container_id == sea.container_id),
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
