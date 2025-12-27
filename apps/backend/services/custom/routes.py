import asyncio
import datetime

from backend.database import database
from backend.mapper_decorator import apply_mapper
from sqlalchemy import and_, select
from sqlalchemy.orm import aliased, contains_eager, joinedload

from .mappers.routes import map_routes
from .models import DropModel, PriceModel, RouteModel, RouteTypeEnum


async def _execute_query(q):
    async with database.session() as session:
        result = (await session.execute(q)).unique()
    return result.all()


def build_usual_query(route_type, date, start_point_id, end_point_id, container_ids):
    return (  # noqa: ECE001
        select(RouteModel)
        .where(
            (RouteModel.effective_from <= date)
            & (RouteModel.effective_to >= date)
            & (RouteModel.start_point_id == start_point_id)
            & (RouteModel.end_point_id == end_point_id)
            & (RouteModel.type == route_type)
        )
        .join(
            PriceModel,
            (RouteModel.id == PriceModel.route_id)
            & PriceModel.container_id.in_(container_ids)
        )
        .options(
            joinedload(RouteModel.start_point),
            joinedload(RouteModel.end_point),
            joinedload(RouteModel.company),
            contains_eager(RouteModel.prices).joinedload(PriceModel.container),
        )
    )


def build_mixed_with_drop_query(date, start_point_id, end_point_id, container_ids):
    return (  # noqa: ECE001
        select(RouteModel)
        .where(
            (RouteModel.effective_from <= date)
            & (RouteModel.effective_to >= date)
            & (RouteModel.start_point_id == start_point_id)
            & (RouteModel.end_point_id == end_point_id)
            & (RouteModel.type == RouteTypeEnum.SEA_RAIL)
        )
        .join(
            PriceModel,
            (RouteModel.id == PriceModel.route_id)
            & PriceModel.container_id.in_(container_ids)
        )
        .join(
            DropModel,
            and_(
                RouteModel.start_point_id == DropModel.sea_start_point_id,
                RouteModel.end_point_id == DropModel.rail_end_point_id,
                RouteModel.company_id == DropModel.company_id,
                PriceModel.container_id == DropModel.container_id,
                DropModel.rail_start_point_id.is_(None),
                DropModel.sea_end_point_id.is_(None)
            )
        )
        .options(
            joinedload(RouteModel.start_point),
            joinedload(RouteModel.end_point),
            joinedload(RouteModel.company),
            contains_eager(RouteModel.prices).joinedload(PriceModel.container),
        )
        .add_columns(DropModel)
    )


def _create_aliases():
    SeaRoute = aliased(RouteModel, name="sea_route")
    RailRoute = aliased(RouteModel, name="rail_route")
    SeaPrice = aliased(PriceModel, name="sea_price")
    RailPrice = aliased(PriceModel, name="rail_price")
    return SeaRoute, RailRoute, SeaPrice, RailPrice


def build_base_sea_rail_query(
    date: datetime.date,
    start_point_id: int,
    end_point_id: int,
    container_ids: list[int]
) -> tuple:
    SeaRoute, RailRoute, SeaPrice, RailPrice = _create_aliases()

    query = (  # noqa: ECE001
        select(SeaRoute, RailRoute)
        .where(
            (SeaRoute.type == RouteTypeEnum.SEA)
            & (RailRoute.type == RouteTypeEnum.RAIL)
            & (SeaRoute.effective_from <= date)
            & (SeaRoute.effective_to >= date)
            & (RailRoute.effective_from <= date)
            & (RailRoute.effective_to >= date)
            & (SeaRoute.start_point_id == start_point_id)
            & (RailRoute.end_point_id == end_point_id)
            & SeaPrice.container_id.in_(container_ids)
            & RailPrice.container_id.in_(container_ids)
        )
        .join(SeaPrice, SeaRoute.id == SeaPrice.route_id)
        .join(RailRoute, SeaRoute.end_point_id == RailRoute.start_point_id)
        .join(RailPrice, RailRoute.id == RailPrice.route_id)
        .options(
            joinedload(SeaRoute.start_point),
            joinedload(SeaRoute.end_point),
            joinedload(SeaRoute.company),
            contains_eager(SeaRoute.prices, alias=SeaPrice).joinedload(PriceModel.container),
            joinedload(RailRoute.start_point),
            joinedload(RailRoute.end_point),
            joinedload(RailRoute.company),
            contains_eager(RailRoute.prices, alias=RailPrice).joinedload(PriceModel.container),
        )
    )

    return query, SeaRoute, RailRoute, SeaPrice, RailPrice


def _add_drop_join(query, condition):
    return query.add_columns(DropModel).join(DropModel, condition)


def create_sea_rail_queries(
    date: datetime.date,
    start_point_id: int,
    end_point_id: int,
    container_ids: list[int]
) -> list:
    base_query, SeaRoute, RailRoute, SeaPrice, RailPrice = build_base_sea_rail_query(
        date, start_point_id, end_point_id, container_ids
    )

    query_all_drop = _add_drop_join(
        base_query,
        and_(
            RailRoute.start_point_id == DropModel.rail_start_point_id,
            RailRoute.end_point_id == DropModel.rail_end_point_id,
            RailRoute.company_id == DropModel.company_id,
            RailPrice.container_id == DropModel.container_id,
            SeaRoute.start_point_id == DropModel.sea_start_point_id,
            SeaRoute.end_point_id == DropModel.sea_end_point_id
        )
    )

    query_rail_drop = _add_drop_join(
        base_query,
        and_(
            RailRoute.start_point_id == DropModel.rail_start_point_id,
            RailRoute.end_point_id == DropModel.rail_end_point_id,
            RailRoute.company_id == DropModel.company_id,
            RailPrice.container_id == DropModel.container_id,
            DropModel.sea_start_point_id.is_(None),
            DropModel.sea_end_point_id.is_(None)
        )
    )

    query_sea_drop = _add_drop_join(
        base_query,
        and_(
            SeaRoute.start_point_id == DropModel.sea_start_point_id,
            SeaRoute.end_point_id == DropModel.sea_end_point_id,
            SeaRoute.company_id == DropModel.company_id,
            SeaPrice.container_id == DropModel.container_id,
            DropModel.rail_start_point_id.is_(None),
            DropModel.rail_end_point_id.is_(None)
        )
    )

    query_no_drop = base_query

    return [query_all_drop, query_rail_drop, query_sea_drop, query_no_drop]


def process_results(results: list) -> list:
    flat_result: list = []
    seen_ids: set[tuple[int, ...]] = set()

    for result in results:
        if not result or isinstance(result, BaseException):
            if isinstance(result, BaseException):
                print(f"Query error: {result}")
            continue

        for row in result:
            has_drop = isinstance(row[-1], DropModel) if row else False
            routes = row[:-1] if has_drop else row

            ids = tuple(segment.id for segment in routes)

            if ids not in seen_ids:
                seen_ids.add(ids)
                flat_result.append(row)

    return flat_result


@apply_mapper(map_routes)
async def find_all_paths(
    date: datetime.date,
    start_point_id: int,
    end_point_id: int,
    container_ids: list[int],
) -> list[dict]:
    query_rail = build_usual_query(
        RouteTypeEnum.RAIL, date, start_point_id, end_point_id, container_ids
    )
    query_sea = build_usual_query(
        RouteTypeEnum.SEA, date, start_point_id, end_point_id, container_ids
    )
    query_mixed = build_usual_query(
        RouteTypeEnum.SEA_RAIL, date, start_point_id, end_point_id, container_ids
    )

    query_mixed_with_drop = build_mixed_with_drop_query(
        date, start_point_id, end_point_id, container_ids
    )

    sea_rail_queries = create_sea_rail_queries(
        date, start_point_id, end_point_id, container_ids
    )

    all_queries = [
        query_rail,
        query_sea,
        query_mixed,
        query_mixed_with_drop,
    ] + sea_rail_queries

    coroutines = [_execute_query(query) for query in all_queries]
    results = await asyncio.gather(*coroutines, return_exceptions=True)

    return process_results(results)
