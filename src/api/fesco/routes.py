import datetime
import os

import aiohttp


async def get_routes(date: datetime.date, departure_id: str, destination_id: str, wte_id: str, lang: str):
    async with aiohttp.ClientSession() as session:
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
        data_to = await resp.json()
    return data_to.get('data')
