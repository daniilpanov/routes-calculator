from typing import List

import datetime
import os

import aiohttp
import asyncio


_segment_types = {
    1: 'rail',
    2: 'sea',
    3: 'truck',
}


def _transform_item(route):
    return {
        'dateFrom': route['DateFrom'],
        'dateTo': route['DateTo'],
        'beginCond': route['BeginCond'],
        'finishCond': route['FinishCond'],
        'containers': [{'name': container['ContainerName']} for container in route.get('Containers', [])],
        'segments': [{
            'segmentOrder': segment['SegmentOrder'],
            'type': _segment_types.get(segment['SegmentType']),
            'from': {'name': segment['BeginLocName']},
            'to': {'name': segment['FinishLocName']},
            'containers': [{
                'containerId': container['ContainerCode'],
                'price': container['Price'],
                'currency': container['Currency'],
            } for container in segment.get('Containers', [])]
        } for segment in route.get('Segments', [])],
    }


async def _get_routes(date: datetime.date, departure_id: str, destination_id: str, wte_id: str, lang: str, session):
    resp = await session.get(
        'https://my.fesco.com/api/v2/lk/offers/fit?date={}&from={}&to={}&wte={}&co=COC'.format(
            date.isoformat(), departure_id, destination_id, wte_id,
        ),
        headers={
            'Accept': 'application/json',
            'Authorization': 'Bearer {}'.format(os.environ.get('FESCO_API_KEY')),
            'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.0.0 Safari/537.36',
            'X-Lk-Lang': lang,
        },
    )
    resp.raise_for_status()
    routes = (await resp.json()).get('data', [])

    return map(_transform_item, routes)


async def find_all_paths(date: datetime.date, departure_id: str, destination_id: str, wte_ids: List[str], lang: str):
    async with aiohttp.ClientSession() as session:
        coroutines = [_get_routes(date, departure_id, destination_id, wte_id, lang, session) for wte_id in wte_ids]
        res = await asyncio.gather(*coroutines, return_exceptions=True)
    routes = []
    for routes_group in res:
        if not isinstance(routes_group, Exception):
            routes.extend(routes_group)
    return routes
