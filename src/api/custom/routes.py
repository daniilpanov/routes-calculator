from sqlalchemy import select, func, cast, String
from sqlalchemy.orm import aliased
from typing import List, Dict

from src.database import database
from .models import RouteModel, PriceModel

async def find_all_paths(
        start_point_id: int,
        end_point_id: int,
        container_id: int,
        price_type: str,
        max_depth: int = 10,
) -> List[Dict]:
    Route = aliased(RouteModel, name='r')
    Price = aliased(PriceModel, name='p')

    # Базовый запрос с явным приведением типов
    base_query = (
        select(
            Route.start_point_id.label('current_start'),
            Route.end_point_id.label('current_end'),
            Price.price.label('total_price'),
            cast(func.concat(
                func.cast(Route.start_point_id, String), ',',
                func.cast(Route.end_point_id, String),
            ), String).label('path'),
            cast(func.concat(
                ',', func.cast(Route.start_point_id, String), ',',
                func.cast(Route.end_point_id, String), ',',
            ), String).label('visited'),
            func.literal(1).label('depth'),
        )
        .join(Price, Route.id == Price.route_id)
        .where(
            Route.start_point_id == start_point_id,
            Price.container_id == container_id,
            Price.price_type == price_type,
        )
    )

    # Рекурсивный CTE
    paths = base_query.cte(name='paths', recursive=True)

    # Рекурсивная часть с проверкой циклов
    recursive_query = (
        select(
            Route.start_point_id.label('current_start'),
            Route.end_point_id.label('current_end'),
            (paths.c.total_price + Price.price).label('total_price'),
            cast(func.concat(
                paths.c.path, ',',
                func.cast(Route.end_point_id, String),
            ), String).label('path'),
            cast(func.concat(
                paths.c.visited,
                func.cast(Route.end_point_id, String), ',',
            ), String).label('visited'),
            (paths.c.depth + 1).label('depth'),
        )
        .join(Price, Route.id == Price.route_id)
        .join(paths, paths.c.current_end == Route.start_point_id)
        .where(
            paths.c.depth < max_depth,
            ~paths.c.visited.contains(f',{Route.end_point_id},'),
            paths.c.current_end != end_point_id,
        )
    )

    # Объединенный CTE
    paths_cte = paths.union_all(recursive_query)

    # Финальный запрос с сортировкой по цене и длине пути
    final_query = (
        select(
            paths_cte.c.path,
            paths_cte.c.total_price,
            paths_cte.c.depth,
        )
        .where(paths_cte.c.current_end == end_point_id)
        .order_by(
            paths_cte.c.total_price,  # Основная сортировка по стоимости
            paths_cte.c.depth,        # Вторичная сортировка по количеству пересадок
        )
    )

    async with database.session() as session:
        result = await session.execute(final_query)
        data = [{
            'path': list(map(int, row.path.split(','))),
            'total_price': float(row.total_price),
            'hops': row.depth
        } for row in result]
    return data
