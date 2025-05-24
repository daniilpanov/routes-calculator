from importlib.util import find_spec

if find_spec('dotenv') is not None:
    from dotenv import load_dotenv
    load_dotenv()

import asyncio
import datetime

from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi import HTTPException
from starlette.status import HTTP_400_BAD_REQUEST, HTTP_500_INTERNAL_SERVER_ERROR

from pycbrf.toolbox import ExchangeRates

from .form_requests import CalculateFormRequest
from .api import fesco

app = FastAPI()
app.mount('/res', StaticFiles(directory='res'), name='res')
app.mount('/lib', StaticFiles(directory='lib'), name='lib')
templates = Jinja2Templates(directory='.')


def union_country_and_name(country, name):
    if country and name:
        return country + ', ' + name
    return name or country


class Converter:
    @classmethod
    def create_with_ru(cls, conversion_rates, plus_percents=0):
        inst = cls(conversion_rates, plus_percents)
        inst.conversion_rates['RUB'] = 1
        inst.conversion_rates['RUR'] = 1
        return inst

    def __init__(self, conversion_rates, plus_percents=0):
        self.conversion_rates = conversion_rates
        self.plus_percents = plus_percents

    def _convert(self, value, from_currency, to_currency):
        value = float(value)
        value += value * self.plus_percents / 100
        return value * self.conversion_rates[from_currency] / self.conversion_rates[to_currency]

    def recursive_currency_convertion(self, obj, needle_currency):
        if isinstance(obj, (list, tuple, set)):
            return [self.recursive_currency_convertion(item, needle_currency) for item in obj]
        elif isinstance(obj, dict):
            if 'Currency' in obj and 'Price' in obj:
                obj['Price'] = self._convert(obj['Price'], obj['Currency'], needle_currency)
                obj['Currency'] = needle_currency
            return dict((i, self.recursive_currency_convertion(v, needle_currency)) for i, v in obj.items())
        return obj


@app.get('/get_departures')
async def all_departure_by_date(date: datetime.date):
    prepared_from = dict()
    # from FESCO
    data_from = await fesco.get_departure_points_by_date(date, 'ru')
    prepared_from.update(map(lambda x: (union_country_and_name(x.get('country'), x.get('name')), x['id']), data_from))

    return prepared_from


@app.get('/get_destinations')
async def all_destination_by_date(date: datetime.date, departure_point_id: str):
    prepared_to = dict()
    # from FESCO
    data_to = await fesco.get_destination_points_by_date(date, departure_point_id, 'ru')
    prepared_to.update(map(lambda x: (x['country'] + ', ' + x['name'], x['id']), data_to))

    return prepared_to


@app.get('/get_rates')
def get_rates(dt_now: datetime.datetime = None):
    if dt_now is None:
        dt_now = datetime.datetime.now()
    rates = ExchangeRates(dt_now)
    return {currency.code: float(currency.value) for currency in rates.rates}


@app.get('/')
async def home(request: Request):
    dt_now = datetime.datetime.now()
    points_from = await all_departure_by_date(dt_now.date())
    parsed_rates = get_rates(dt_now)
    return templates.TemplateResponse('index.html', {
        'request': request,
        'rates': dict(parsed_rates),
        'points_from': points_from,
    })


@app.post('/calculate')
async def calculate(request: CalculateFormRequest):
    dtc = datetime.date.today()
    containers = await fesco.get_containers(dtc, request.departureId, request.destinationId, 'ru')
    container_ids = fesco.search_container_ids(containers, request.cargoWeight, request.containerType)
    if not container_ids:
        raise HTTPException(status_code=HTTP_400_BAD_REQUEST, detail='No container found')
    try:
        routes_groups = await asyncio.gather(*(fesco.get_routes(dtc, request.departureId, request.destinationId, container_id, 'ru') for container_id in container_ids))
        routes = []
        for route_group in routes_groups:
            routes.extend(route_group)
        parsed_rates = get_rates(datetime.datetime.combine(dtc, datetime.time()))
        return Converter.create_with_ru(parsed_rates).recursive_currency_convertion(routes, request.currency)
    except Exception as e:
        raise HTTPException(status_code=HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)) from e
