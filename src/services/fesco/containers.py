import datetime
import os
import re

import aiohttp


async def get_containers(date: datetime.date, departure_id: str, destination_id: str, lang: str):
    async with aiohttp.ClientSession() as session:
        resp = await session.get(
            'https://my.fesco.com/api/v2/lk/offers/fit/wte?date={}&from={}&to={}'.format(
                date.isoformat(), departure_id, destination_id,
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


def search_container_ids(containers: list, weight: int, size: int):
    seeking_expr = re.compile(r'^(\d+)-.+[^ 0-9](\d+)t$')
    containers_map = {}
    containers_variants = []
    unweighted_containers_variants = []
    needle = []

    for container in containers:
        try:
            r1 = seeking_expr.match(container['ContainerNameEng'])
            if r1:
                csize, cweight = map(int, r1.groups())
                containers_variants.append((csize, cweight))
            else:
                csize = int(container['ContainerNameEng'].strip().split('-', maxsplit=1)[0])
                cweight = None
                unweighted_containers_variants.append(csize)
        except Exception as e:
            print(e)
            continue
        containers_map[(csize, cweight)] = container['ContainerCode']

    containers_variants.sort()
    unweighted_containers_variants.sort()

    for csize, cweight in containers_variants:
        if csize >= size and cweight >= weight:
            needle.append(containers_map[(csize, cweight)])
            break
    for csize in unweighted_containers_variants:
        if csize >= size:
            needle.append(containers_map[(csize, None)])
            break

    return needle
