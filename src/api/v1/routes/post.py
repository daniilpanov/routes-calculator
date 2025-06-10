import datetime
from functools import lru_cache

from fastapi import APIRouter, HTTPException
from starlette.status import HTTP_400_BAD_REQUEST, HTTP_500_INTERNAL_SERVER_ERROR

from src.services import fesco
from src.utils.currency_converter import Converter
from .models.form_requests import CalculateFormRequest
from ..rates.get import get_rates

router = APIRouter(prefix='/v1/routes', tags=['routes'])


@lru_cache(1024)
@router.post('/calculate')
async def calculate(request: CalculateFormRequest):
    dtc = datetime.date.today()
    containers = await fesco.get_containers(dtc, request.departureId, request.destinationId, 'ru')
    container_ids = fesco.search_container_ids(containers, request.cargoWeight, request.containerType)
    if not container_ids:
        raise HTTPException(status_code=HTTP_400_BAD_REQUEST, detail='No container found')
    try:
        routes = await fesco.find_all_paths(dtc, request.departureId, request.destinationId, container_ids, 'ru')
        parsed_rates = get_rates(datetime.datetime.combine(dtc, datetime.time()))
        routes = Converter(parsed_rates).recursive_currency_convertion(routes, request.currency)
        summed_routes = []
        for route in routes:
            sum_containers = 0
            for segment in route['segments']:
                for container in segment['containers']:
                    sum_containers += container['price']
            route['price'] = sum_containers
            summed_routes.append(route)
        summed_routes.sort(key=lambda item: item['price'])
        return summed_routes
    except Exception as e:
        raise HTTPException(status_code=HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)) from e
