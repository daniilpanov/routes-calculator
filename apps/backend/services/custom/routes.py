import asyncio
import datetime

from backend.database import database
from backend.mapper_decorator import apply_mapper
from sqlalchemy import select
from sqlalchemy.orm import joinedload

from .mappers.routes import map_routes
from .models import DropModel, RailRouteModel, SeaRouteModel


async def _execute_query(q):
    async with database.session() as session:
        result = await session.execute(q)
    return result.all()


def build_usual_query(route_class, date, start_point_id, end_point_id, container_ids):
    return (  # noqa: ECE001
        select(route_class)
        .where(
            (route_class.effective_from <= date)
            & (route_class.effective_to >= date)
            & (route_class.start_point_id == start_point_id)
            & (route_class.end_point_id == end_point_id)
            & route_class.container_id.in_(container_ids)
        )
        .options(
            joinedload(route_class.start_point),
            joinedload(route_class.end_point),
            joinedload(route_class.company),
            joinedload(route_class.container),
        )
    )


def build_cross_query(date, start_point_id, end_point_id, container_ids, with_drop: bool = True):
    return (  # noqa: ECE001
        (select(SeaRouteModel, RailRouteModel, DropModel) if with_drop else select(SeaRouteModel, RailRouteModel))
        .where(
            (SeaRouteModel.effective_from <= date)
            & (SeaRouteModel.effective_to >= date)
            & (RailRouteModel.effective_from <= date)
            & (RailRouteModel.effective_to >= date)
            & (SeaRouteModel.start_point_id == start_point_id)
            & (RailRouteModel.end_point_id == end_point_id)
            & SeaRouteModel.container_id.in_(container_ids)
        )
        .join(
            RailRouteModel,
            (SeaRouteModel.end_point_id == RailRouteModel.start_point_id)
            & (SeaRouteModel.container_id == RailRouteModel.container_id),
        )
        .options(
            joinedload(SeaRouteModel.start_point),
            joinedload(SeaRouteModel.end_point),
            joinedload(SeaRouteModel.company),
            joinedload(SeaRouteModel.container),
            joinedload(RailRouteModel.start_point),
            joinedload(RailRouteModel.end_point),
            joinedload(RailRouteModel.company),
            joinedload(RailRouteModel.container),
        )
    )


@apply_mapper(map_routes)
async def find_all_paths(
    date: datetime.date,
    start_point_id: int,
    end_point_id: int,
    container_ids: list[int],
) -> list[dict]:
    query_rail = build_usual_query(RailRouteModel, date, start_point_id, end_point_id, container_ids)
    query_sea = build_usual_query(SeaRouteModel, date, start_point_id, end_point_id, container_ids)

    query_sea_rail_drop_all = build_cross_query(  # noqa: ECE001
        date,
        start_point_id,
        end_point_id,
        container_ids,
    ).join(
        DropModel,
        (RailRouteModel.start_point_id == DropModel.rail_start_point_id)
        & (RailRouteModel.end_point_id == DropModel.rail_end_point_id)
        & (RailRouteModel.company_id == DropModel.company_id)
        & (RailRouteModel.container_id == DropModel.container_id)
        & (SeaRouteModel.start_point_id == DropModel.sea_start_point_id)
        & (SeaRouteModel.end_point_id == DropModel.sea_end_point_id)
    )
    query_sea_rail_drop_rail = build_cross_query(  # noqa: ECE001
        date,
        start_point_id,
        end_point_id,
        container_ids,
    ).join(
        DropModel,
        (RailRouteModel.start_point_id == DropModel.rail_start_point_id)
        & (RailRouteModel.end_point_id == DropModel.rail_end_point_id)
        & (RailRouteModel.company_id == DropModel.company_id)
        & (RailRouteModel.container_id == DropModel.container_id)
        & (DropModel.sea_start_point_id == None)  # noqa: E711
        & (DropModel.sea_end_point_id == None)  # noqa: E711
    )
    query_sea_rail_drop_sea = build_cross_query(  # noqa: ECE001
        date,
        start_point_id,
        end_point_id,
        container_ids,
    ).join(
        DropModel,
        (SeaRouteModel.start_point_id == DropModel.sea_start_point_id)
        & (SeaRouteModel.end_point_id == DropModel.sea_end_point_id)
        & (SeaRouteModel.company_id == DropModel.company_id)
        & (SeaRouteModel.container_id == DropModel.container_id)
        & (DropModel.rail_start_point_id == None)  # noqa: E711
        & (DropModel.rail_end_point_id == None)  # noqa: E711
    )
    query_sea_rail_no_drop = build_cross_query(date, start_point_id, end_point_id, container_ids, False)

    all_queries = [
        query_rail,
        query_sea,
        query_sea_rail_drop_all,
        query_sea_rail_drop_rail,
        query_sea_rail_drop_sea,
        query_sea_rail_no_drop,
    ]

    coroutines = [_execute_query(query) for query in all_queries]
    results = await asyncio.gather(*coroutines, return_exceptions=True)

    flat_result: list[dict] = []
    segment_ids_set = set()

    for r in results:
        if r and not isinstance(r, BaseException):
            for route in r:
                route_without_drop = route[:-1] if isinstance(route[-1], DropModel) else route

                ids = (segment.id for segment in route_without_drop)
                if ids not in segment_ids_set:
                    segment_ids_set.add(ids)
                    flat_result.append(route)

    return flat_result
