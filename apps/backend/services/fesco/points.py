import datetime

import aiohttp
from backend.config import get_settings
from backend.mapper_decorator import apply_mapper

from .mappers.points import map_points


@apply_mapper(map_points)
async def get_departure_points_by_date(date: datetime.date):
    async with aiohttp.ClientSession() as session:
        resp = await session.get(
            f"https://api.fesco.com/api/v1/lk/calc/fit/from?date={date.isoformat()}",
            headers={
                "Authorization": f"Bearer {get_settings().FESCO_API_KEY}",
                "X-Lk-Lang": "RU",
            },
        )
        resp.raise_for_status()
        data_from = await resp.json()
    return data_from.get("data")


@apply_mapper(map_points)
async def get_destination_points_by_date(date: datetime.date, departure_point_id: str):
    async with aiohttp.ClientSession() as session:
        resp = await session.get(
            f"https://api.fesco.com/api/v1/lk/calc/fit/to"
            f"?date={date.isoformat()}&from={departure_point_id}",
            headers={
                "Authorization": f"Bearer {get_settings().FESCO_API_KEY}",
                "X-Lk-Lang": "RU",
            },
        )
        resp.raise_for_status()
        data_to = await resp.json()
    return data_to.get("data")
