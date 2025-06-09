import datetime
import os

import aiohttp


async def get_departure_points_by_date(date: datetime.date, lang: str):
    async with aiohttp.ClientSession() as session:
        resp = await session.get(
            'https://api.fesco.com/api/v1/lk/calc/fit/from?date={}'.format(date.isoformat()),
            headers={
                'Authorization': 'Bearer {}'.format(os.environ.get('FESCO_API_KEY')),
                'X-Lk-Lang': lang,
            },
        )
        resp.raise_for_status()
        data_from = await resp.json()
    return data_from.get('data')


async def get_destination_points_by_date(date: datetime.date, departure_point_id: str, lang: str):
    async with aiohttp.ClientSession() as session:
        resp = await session.get(
            'https://api.fesco.com/api/v1/lk/calc/fit/to?date={}&from={}'.format(date.isoformat(), departure_point_id),
            headers={
                'Authorization': 'Bearer {}'.format(os.environ.get('FESCO_API_KEY')),
                'X-Lk-Lang': lang,
            },
        )
        resp.raise_for_status()
        data_to = await resp.json()
    return data_to.get('data')
