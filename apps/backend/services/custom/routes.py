import asyncio
import datetime

from backend.mapper_decorator import apply_mapper
from shared.database import Base, get_database
from shared.models import DropModel, PriceModel, RouteModel, RouteTypeEnum
from sqlalchemy import and_, desc, select
from sqlalchemy.orm import aliased, contains_eager, joinedload

from .mappers.routes import map_routes


async def _execute_query(q):
    async with get_database().session_context() as session:
        result = (await session.execute(q)).unique()
    return result.all()


def build_usual_query(
    route_type: RouteTypeEnum,
    date: datetime.date,
    start_point_id: int,
    end_point_id: int,
    container_ids: list[int],
    only_in_selected_date_range: bool = True,
):
    where_clause = and_(
        RouteModel.effective_from <= date,
        RouteModel.start_point_id == start_point_id,
        RouteModel.end_point_id == end_point_id,
        RouteModel.type == route_type,
    )
    if only_in_selected_date_range:
        where_clause &= RouteModel.effective_to >= date

    return (
        select(RouteModel)
        .where(where_clause)
        .join(
            PriceModel,
            and_(
                RouteModel.id == PriceModel.route_id,
                PriceModel.container_id.in_(container_ids),
            ),
        )
        .order_by(desc(RouteModel.effective_to))
        # note: I tried using 'group by' statement, but it cuts off prices
        .options(
            joinedload(RouteModel.start_point),
            joinedload(RouteModel.end_point),
            joinedload(RouteModel.company),
            contains_eager(RouteModel.prices).joinedload(PriceModel.container),
        )
    )


def build_mixed_with_drop_query(
    date: datetime.date,
    start_point_id: int,
    end_point_id: int,
    container_ids: list[int],
    only_in_selected_date_range: bool = False,
):
    where_clause = and_(
        RouteModel.effective_from <= date,
        RouteModel.start_point_id == start_point_id,
        RouteModel.end_point_id == end_point_id,
        RouteModel.type == RouteTypeEnum.SEA_RAIL,
    )
    if only_in_selected_date_range:
        where_clause &= RouteModel.effective_to >= date

    return (  # noqa: ECE001
        select(RouteModel)
        .where(where_clause)
        .join(
            PriceModel,
            and_(
                RouteModel.id == PriceModel.route_id,
                PriceModel.container_id.in_(container_ids),
            ),
        )
        .join(
            DropModel,
            and_(
                RouteModel.start_point_id == DropModel.sea_start_point_id,
                RouteModel.end_point_id == DropModel.rail_end_point_id,
                RouteModel.company_id == DropModel.company_id,
                PriceModel.container_id == DropModel.container_id,
                DropModel.rail_start_point_id.is_(None),
                DropModel.sea_end_point_id.is_(None),
                DropModel.effective_from <= RouteModel.effective_from,
                DropModel.effective_to >= RouteModel.effective_to,
            ),
        )
        .order_by(desc(RouteModel.effective_to))
        # note: I tried using 'group by' statement, but it cuts off prices
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
    container_ids: list[int],
    only_in_selected_date_range: bool = False,
) -> tuple:
    SeaRoute, RailRoute, SeaPrice, RailPrice = _create_aliases()
    where_clause = and_(
        SeaRoute.type == RouteTypeEnum.SEA,
        RailRoute.type == RouteTypeEnum.RAIL,
        SeaRoute.effective_from <= date,
        RailRoute.effective_from <= date,
        SeaRoute.start_point_id == start_point_id,
        RailRoute.end_point_id == end_point_id,
        SeaPrice.container_id.in_(container_ids),
        RailPrice.container_id.in_(container_ids),
    )
    if only_in_selected_date_range:
        where_clause &= SeaRoute.effective_to >= date
        where_clause &= RailRoute.effective_to >= date

    query = (  # noqa: ECE001
        select(SeaRoute, RailRoute)
        .where(where_clause)
        .join(SeaPrice, SeaRoute.id == SeaPrice.route_id)
        .join(RailRoute, SeaRoute.end_point_id == RailRoute.start_point_id)
        .join(RailPrice, RailRoute.id == RailPrice.route_id)
        .order_by(desc(SeaRoute.effective_to), desc(RailRoute.effective_to))
        # here could be 'group_by', but it doesn't work correctly with 'joinedload'
        # so we select unique on the client-side
        # note: I tried using 'group by' statement, but it cuts off prices
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
    container_ids: list[int],
    only_in_selected_date_range: bool = False,
) -> list:
    base_query, SeaRoute, RailRoute, SeaPrice, RailPrice = build_base_sea_rail_query(
        date, start_point_id, end_point_id, container_ids, only_in_selected_date_range
    )

    query_all_drop = _add_drop_join(
        base_query,
        and_(
            RailRoute.start_point_id == DropModel.rail_start_point_id,
            RailRoute.end_point_id == DropModel.rail_end_point_id,
            RailRoute.company_id == DropModel.company_id,
            RailPrice.container_id == DropModel.container_id,
            SeaRoute.start_point_id == DropModel.sea_start_point_id,
            SeaRoute.end_point_id == DropModel.sea_end_point_id,
            DropModel.effective_from <= SeaRoute.effective_from,
            DropModel.effective_to >= SeaRoute.effective_to,
            DropModel.effective_from <= RailRoute.effective_from,
            DropModel.effective_to >= RailRoute.effective_to,
        ),
    )

    query_rail_drop = _add_drop_join(
        base_query,
        and_(
            RailRoute.start_point_id == DropModel.rail_start_point_id,
            RailRoute.end_point_id == DropModel.rail_end_point_id,
            RailRoute.company_id == DropModel.company_id,
            RailPrice.container_id == DropModel.container_id,
            DropModel.sea_start_point_id.is_(None),
            DropModel.sea_end_point_id.is_(None),
            DropModel.effective_from <= SeaRoute.effective_from,
            DropModel.effective_to >= SeaRoute.effective_to,
            DropModel.effective_from <= RailRoute.effective_from,
            DropModel.effective_to >= RailRoute.effective_to,
        ),
    )

    query_sea_drop = _add_drop_join(
        base_query,
        and_(
            SeaRoute.start_point_id == DropModel.sea_start_point_id,
            SeaRoute.end_point_id == DropModel.sea_end_point_id,
            SeaRoute.company_id == DropModel.company_id,
            SeaPrice.container_id == DropModel.container_id,
            DropModel.rail_start_point_id.is_(None),
            DropModel.rail_end_point_id.is_(None),
            DropModel.effective_from <= SeaRoute.effective_from,
            DropModel.effective_to >= SeaRoute.effective_to,
            DropModel.effective_from <= RailRoute.effective_from,
            DropModel.effective_to >= RailRoute.effective_to,
        ),
    )

    query_no_drop = base_query

    return [query_all_drop, query_rail_drop, query_sea_drop, query_no_drop]


def process_results(
    results: list[list[list[Base]] | BaseException],
    date: datetime.date,
) -> list[tuple[list[Base], bool]]:
    flat_result: list = []
    seen_ids: set[tuple[tuple[int, int, int], ...]] = set()

    for result in results:
        if not result or isinstance(result, BaseException):
            if isinstance(result, BaseException):
                print(f"Query error: {result}")
            continue

        for row in result:
            if not row:
                continue

            routes: list[RouteModel] = row[:-1] if isinstance(row[-1], DropModel) else row

            uids = tuple((
                segment.company_id,
                segment.start_point_id,
                segment.end_point_id,
            ) for segment in routes)

            if uids in seen_ids:
                continue

            may_route_be_invalid = False
            for segment in routes:
                if segment.effective_to.date() < date:
                    may_route_be_invalid = True
                    break

            seen_ids.add(uids)
            flat_result.append((row, may_route_be_invalid))

    return flat_result


@apply_mapper(map_routes)
async def find_all_paths(
    date: datetime.date,
    start_point_id: int,
    end_point_id: int,
    container_ids: list[int],
    only_in_selected_date_range: bool = False,
) -> list[tuple[list[Base], bool]]:
    query_rail = build_usual_query(
        RouteTypeEnum.RAIL, date, start_point_id, end_point_id, container_ids, only_in_selected_date_range
    )
    query_sea = build_usual_query(
        RouteTypeEnum.SEA, date, start_point_id, end_point_id, container_ids, only_in_selected_date_range
    )
    query_mixed = build_usual_query(
        RouteTypeEnum.SEA_RAIL, date, start_point_id, end_point_id, container_ids, only_in_selected_date_range
    )

    query_mixed_with_drop = build_mixed_with_drop_query(
        date, start_point_id, end_point_id, container_ids, only_in_selected_date_range
    )

    sea_rail_queries = create_sea_rail_queries(
        date, start_point_id, end_point_id, container_ids, only_in_selected_date_range
    )

    all_queries = [
        query_rail,
        query_sea,
        query_mixed_with_drop,
        query_mixed,
    ] + sea_rail_queries

    coroutines = [_execute_query(query) for query in all_queries]
    results = await asyncio.gather(*coroutines, return_exceptions=True)

    return process_results(results, date)
