import datetime

import aiohttp
from backend.config import get_settings
from backend.mapper_decorator import apply_mapper

from .mappers.containers import map_containers


@apply_mapper(map_containers)
async def get_containers(date: datetime.date, departure_id: str, destination_id: str):
    async with aiohttp.ClientSession() as session:
        resp = await session.get(
            "https://my.fesco.com/api/v2/lk/offers/fit/wte?date={}&from={}&to={}".format(
                date.isoformat(),
                departure_id,
                destination_id,
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
        data_to = await resp.json()
    return data_to.get("data")


def search_container_ids(containers: list, weight: int, container_type: int):
    needle = []

    for container in containers:
        if container["size"] == container_type:
            if container["weight_to"]:
                if container["weight_from"] <= weight <= container["weight_to"]:
                    needle.append(container["id"])
            else:
                needle.append(container["id"])

    return needle
