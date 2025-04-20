from dotenv import load_dotenv
from starlette.status import HTTP_400_BAD_REQUEST, HTTP_500_INTERNAL_SERVER_ERROR

load_dotenv()

import datetime

from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi import HTTPException
from pycbrf.toolbox import ExchangeRates

from .requests import CalculateFormRequest
from .api import fesco

app = FastAPI()
app.mount("/res", StaticFiles(directory="res"), name="res")
app.mount("/lib", StaticFiles(directory="lib"), name="lib")
templates = Jinja2Templates(directory="html")


def union_country_and_name(country, name):
    if country and name:
        return country + ', ' + name
    return name or country


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


@app.get('/')
async def home(request: Request):
    dt_now = datetime.datetime.now()
    rates = ExchangeRates(dt_now)
    parsed_rates = {currency.code: float(currency.value) for currency in rates.rates}
    points_from = await all_departure_by_date(dt_now.date())
    return templates.TemplateResponse('routes-calc-form.html', {
        'request': request,
        'rates': dict(parsed_rates),
        'points_from': points_from,
    })


@app.post('/calculate')
async def calculate(request: CalculateFormRequest):
    dtc = datetime.date.today()
    containers = await fesco.get_containers(dtc, request.departureId, request.destinationId, 'ru')
    container_id = fesco.search_container_id(containers, request.cargoWeight, request.containerType)
    if not container_id:
        raise HTTPException(status_code=HTTP_400_BAD_REQUEST, detail='No container found')
    try:
        return await fesco.get_routes(dtc, request.departureId, request.destinationId, container_id, 'ru')
    except Exception as e:
        raise HTTPException(status_code=HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)) from e
