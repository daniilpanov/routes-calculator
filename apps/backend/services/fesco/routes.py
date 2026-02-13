import asyncio
import datetime

import aiohttp
from backend.config import get_settings
from backend.mapper_decorator import apply_mapper

from .mappers.routes import map_routes


async def _get_routes(
    date: datetime.date,
    departure_id: str,
    destination_id: str,
    wte_id: str,
    session,
):
    resp = await session.get(
        "https://my.fesco.com/api/v2/lk/offers/fit?date={}&from={}&to={}&wte={}&co=COC".format(
            date.isoformat(),
            departure_id,
            destination_id,
            wte_id,
        ),
        headers={
            "Accept": "application/json",
            "Authorization": f"Bearer {get_settings().FESCO_API_KEY}",
            "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
            "(KHTML, like Gecko) Chrome/134.0.0.0 Safari/537.36",
            "X-Lk-Lang": "RU",
        },
    )
    resp.raise_for_status()

    return (await resp.json()).get("data", [])


@apply_mapper(map_routes)
async def find_all_paths(
    date: datetime.date,
    departure_id: str,
    destination_id: str,
    wte_ids: list[str],
    _: bool = False,
):
    async with aiohttp.ClientSession() as session:
        coroutines = [
            _get_routes(date, departure_id, destination_id, wte_id, session)
            for wte_id in wte_ids
        ]
        res = await asyncio.gather(*coroutines, return_exceptions=True)

    routes = []
    for routes_group in res:
        if not isinstance(routes_group, BaseException):
            routes.extend(routes_group)

    return routes
