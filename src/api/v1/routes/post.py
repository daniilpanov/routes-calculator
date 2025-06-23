from functools import lru_cache

from fastapi import APIRouter, HTTPException
from starlette.status import HTTP_400_BAD_REQUEST, HTTP_500_INTERNAL_SERVER_ERROR

from src.services import custom, fesco
from .models.form_requests import CalculateFormRequest

router = APIRouter(prefix='/v1/routes', tags=['routes'])


async def _get_routes(modul, date, dep, dest, cweight, ctype):
    containers = await modul.get_containers(date, dep, dest)
    container_ids = modul.search_container_ids(containers, cweight, ctype)
    if not container_ids:
        return []
    try:
        return await modul.find_all_paths(date, dep, dest, container_ids)
    except Exception as e:
        print(e)
        return []


@router.post('/calculate')
async def calculate(request: CalculateFormRequest):
    routes = []
    if 'FESCO' in request.destinationId:
        routes.extend(await _get_routes(fesco, request.dispatchDate, request.departureId.pop('FESCO'), request.destinationId.pop('FESCO'), request.cargoWeight, request.containerType))
    for service in request.destinationId:
        print(service)
        routes.extend(await _get_routes(custom, request.dispatchDate, request.departureId[service], request.destinationId[service], request.cargoWeight, request.containerType))
    return routes
