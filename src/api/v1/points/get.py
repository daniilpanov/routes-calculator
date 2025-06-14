import datetime
from functools import lru_cache

from fastapi import APIRouter

from src.services import fesco
from src.utils.string_formatters import union_country_and_name

router = APIRouter(prefix='/v1/points', tags=['points'])


@lru_cache(1024)
@router.get('/departures')
async def all_departure_by_date(date: datetime.date):
    prepared_from = dict()
    # from FESCO
    data_from = await fesco.get_departure_points_by_date(date)
    prepared_from.update(map(lambda x: (union_country_and_name(x.get('country'), x.get('name')), x['id']), data_from))

    return prepared_from


@lru_cache(1024)
@router.get('/destinations')
async def all_destination_by_date(date: datetime.date, departure_point_id: str):
    prepared_to = dict()
    # from FESCO
    data_to = await fesco.get_destination_points_by_date(date, departure_point_id)
    prepared_to.update(map(lambda x: (union_country_and_name(x.get('country'), x.get('name')), x['id']), data_to))

    return prepared_to
