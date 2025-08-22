import asyncio
import datetime

from backend.database import database
from backend.mapper_decorator import apply_mapper
from sqlalchemy import select
from sqlalchemy.orm import aliased, joinedload, load_only

from .mappers.routes import map_routes
from .models import PointModel, RailRouteModel, SeaRouteModel


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
            joinedload(rail.start_point).options(
                load_only(PointModel.id, PointModel.parent_id),
                joinedload(PointModel.parent),
            ),
            joinedload(rail.end_point).options(
                load_only(PointModel.id, PointModel.parent_id),
                joinedload(PointModel.parent),
            ),
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
            joinedload(sea.start_point).options(
                load_only(PointModel.id, PointModel.parent_id),
                joinedload(PointModel.parent),
            ),
            joinedload(sea.end_point).options(
                load_only(PointModel.id, PointModel.parent_id),
                joinedload(PointModel.parent),
            ),
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
            joinedload(sea.start_point).options(
                load_only(PointModel.id, PointModel.parent_id),
                joinedload(PointModel.parent),
            ),
            joinedload(sea.end_point).options(
                load_only(PointModel.id, PointModel.parent_id),
                joinedload(PointModel.parent),
            ),
            joinedload(sea.company),
            joinedload(sea.container),
            joinedload(rail.start_point).options(
                load_only(PointModel.id, PointModel.parent_id),
                joinedload(PointModel.parent),
            ),
            joinedload(rail.end_point).options(
                load_only(PointModel.id, PointModel.parent_id),
                joinedload(PointModel.parent),
            ),
            joinedload(rail.company),
            joinedload(rail.container),
        )
    )
    query_rail_sea = (  # noqa: ECE001
        select(rail, sea)
        .where(
            (rail.effective_from <= date)
            & (rail.effective_to >= date)
            & (sea.effective_from <= date)
            & (sea.effective_to >= date)
            & (rail.start_point_id == start_point_id)
            & (sea.end_point_id == end_point_id)
            & rail.container_id.in_(container_ids)
        )
        .join(
            sea,
            (rail.end_point_id == sea.start_point_id)
            & (rail.container_id == sea.container_id),
        )
        .options(
            joinedload(rail.start_point).options(
                load_only(PointModel.id, PointModel.parent_id),
                joinedload(PointModel.parent),
            ),
            joinedload(rail.end_point).options(
                load_only(PointModel.id, PointModel.parent_id),
                joinedload(PointModel.parent),
            ),
            joinedload(rail.company),
            joinedload(rail.container),
            joinedload(sea.start_point).options(
                load_only(PointModel.id, PointModel.parent_id),
                joinedload(PointModel.parent),
            ),
            joinedload(sea.end_point).options(
                load_only(PointModel.id, PointModel.parent_id),
                joinedload(PointModel.parent),
            ),
            joinedload(sea.company),
            joinedload(sea.container),
        )
    )
    query_rail_sea_rail = (  # noqa: ECE001
        select(rail, sea, rail2)
        .where(
            (rail.effective_from <= date)
            & (rail.effective_to >= date)
            & (sea.effective_from <= date)
            & (sea.effective_to >= date)
            & (rail2.effective_from <= date)
            & (rail2.effective_to >= date)
            & (rail.start_point_id == start_point_id)
            & (rail2.end_point_id == end_point_id)
            & rail.container_id.in_(container_ids)
        )
        .join(
            sea,
            (rail.end_point_id == sea.start_point_id)
            & (rail.container_id == sea.container_id),
        )
        .join(
            rail2,
            (sea.end_point_id == rail2.start_point_id)
            & (sea.container_id == rail2.container_id),
        )
        .options(
            joinedload(rail.start_point).options(
                load_only(PointModel.id, PointModel.parent_id),
                joinedload(PointModel.parent),
            ),
            joinedload(rail.end_point).options(
                load_only(PointModel.id, PointModel.parent_id),
                joinedload(PointModel.parent),
            ),
            joinedload(rail.company),
            joinedload(rail.container),
            joinedload(sea.start_point).options(
                load_only(PointModel.id, PointModel.parent_id),
                joinedload(PointModel.parent),
            ),
            joinedload(sea.end_point).options(
                load_only(PointModel.id, PointModel.parent_id),
                joinedload(PointModel.parent),
            ),
            joinedload(sea.company),
            joinedload(sea.container),
            joinedload(rail2.start_point).options(
                load_only(PointModel.id, PointModel.parent_id),
                joinedload(PointModel.parent),
            ),
            joinedload(rail2.end_point).options(
                load_only(PointModel.id, PointModel.parent_id),
                joinedload(PointModel.parent),
            ),
            joinedload(rail2.company),
            joinedload(rail2.container),
        )
    )

    all_queries = [
        query_rail,
        query_sea,
        query_rail_sea,
        query_sea_rail,
        query_rail_sea_rail,
    ]

    coroutines = [_execute_query(query) for query in all_queries]
    results = await asyncio.gather(*coroutines, return_exceptions=True)
    flat_result: list[dict] = []

    for r in results:
        if r and not isinstance(r, BaseException):
            flat_result.extend(r)

    return flat_result
