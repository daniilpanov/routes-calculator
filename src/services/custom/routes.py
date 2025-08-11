import datetime
from typing import Dict, List

import sqlalchemy
from sqlalchemy import select, literal, func
from sqlalchemy.orm import aliased, joinedload, selectinload

from src.database import database
from src.mapper_decorator import apply_mapper
from .mappers.routes import map_routes
from .models.price import PriceTypeModel, RoutePriceModel
from .models.route import RouteModel


async def _execute_query(q):
    async with database.session() as session:
        result = await session.execute(q)
    return result.all()

@apply_mapper(map_routes)
async def find_all_paths(
    date: datetime.date,
    start_point_id: int,
    end_point_id: int,
    container_ids: List[int],
) -> List[List[RouteModel]]:
    Route = aliased(RouteModel)

    base_cte = (
        select(
            Route.id.label("route_id"),
            Route.id.label("last_id"),
            Route.start_point_id,
            Route.end_point_id,
            Route.container_id,
            literal(1).label("depth"),
            func.cast(Route.id, sqlalchemy.String).label("path"),
            func.cast(
                func.concat(Route.start_point_id, '-', Route.end_point_id),
                sqlalchemy.String
            ).label("point_signature"),
            func.cast(Route.container_id, sqlalchemy.String).label("container_path")
        )
        .where(
            Route.effective_from <= date,
            Route.effective_to >= date,
            Route.start_point_id == start_point_id,
            Route.container_id.in_(container_ids),
        )
        .cte(name="path_cte", recursive=True)
    )

    route = aliased(RouteModel)

    recursive_cte = (
        select(
            base_cte.c.route_id,
            route.id.label("last_id"),
            base_cte.c.start_point_id,
            route.end_point_id,
            route.container_id,
            (base_cte.c.depth + 1).label("depth"),
            func.concat(base_cte.c.path, ',', func.cast(route.id, sqlalchemy.String)).label("path"),
            func.concat(base_cte.c.point_signature, ';', route.start_point_id, '-', route.end_point_id).label("point_signature"),
            func.concat(base_cte.c.container_path, ',', func.cast(route.container_id, sqlalchemy.String)).label("container_path")
        )
        .join(
            route,
            (base_cte.c.end_point_id == route.start_point_id)
            & (route.effective_from <= date)
            & (route.effective_to >= date)
            & (route.container_id.in_(container_ids))
        )
        .where(
            base_cte.c.depth < 5,
            ~base_cte.c.point_signature.like(
                func.concat('%', route.start_point_id, '-', route.end_point_id, '%')
            ),
            route.container_id == sqlalchemy.cast(
                func.substring_index(base_cte.c.container_path, ',', -1),
                sqlalchemy.Integer
            )
        )
    )

    path_cte = base_cte.union_all(recursive_cte)

    final_paths_query = (
        select(path_cte)
        .where(path_cte.c.end_point_id == end_point_id)
        .where(
            sqlalchemy.cast(
                func.substring_index(path_cte.c.container_path, ',', 1),
                sqlalchemy.Integer
            ) == sqlalchemy.cast(
                func.substring_index(path_cte.c.container_path, ',', -1),
                sqlalchemy.Integer
            )
        )
    )

    async with database.session() as session:
        paths_result = await session.execute(final_paths_query)
        paths = paths_result.all()

        if not paths:
            return []

        all_route_ids = set()
        for row in paths:
            ids = map(int, row.path.split(','))
            all_route_ids.update(ids)

        routes_query = (
            select(RouteModel)
            .where(RouteModel.id.in_(all_route_ids))
            .options(
                joinedload(RouteModel.start_point),
                joinedload(RouteModel.end_point),
                joinedload(RouteModel.company),
                joinedload(RouteModel.container),
                selectinload(RouteModel.prices).selectinload(RoutePriceModel.price_type),
            )
        )
        routes_result = await session.execute(routes_query)
        routes = routes_result.scalars().all()
        routes_map = {r.id: r for r in routes}

        price_data = await session.execute(
            select(RoutePriceModel, PriceTypeModel)
            .join(PriceTypeModel, PriceTypeModel.id == RoutePriceModel.price_type_id)
            .where(RoutePriceModel.route_id.in_(all_route_ids))
        )
        prices_grouped_by_route: Dict[int, Dict[str, float]] = {}
        for price, price_type in price_data:
            prices_grouped_by_route.setdefault(price.route_id, {})[price_type.name] = float(price.value)

        for route in routes:
            for price_type_name, value in prices_grouped_by_route.get(route.id, {}).items():
                setattr(route, price_type_name, value)

        full_paths = []
        for row in paths:
            route_ids = list(map(int, row.path.split(',')))
            route_path = [routes_map[rid] for rid in route_ids if rid in routes_map]
            full_paths.append(route_path)

        return full_paths

