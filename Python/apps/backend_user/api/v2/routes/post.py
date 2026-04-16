import asyncio
import datetime

from fastapi import APIRouter

from module_data_fesco_api_adapter import api_client
from module_data_internal import aggregators

from .models.form_requests import CalculateFormRequest

router = APIRouter(prefix="/v2/routes", tags=["v2", "routes"])


async def _get_routes(
    modul,
    date: datetime.date,
    departure: str | int,
    destination: str | int,
    container_weight: float,
    container_type: int,
):
    containers = await modul.get_containers(date, departure, destination)
    container_ids = modul.search_container_ids(
        containers, container_weight, container_type
    )
    if not container_ids:
        return []
    try:
        return await modul.find_all_paths(date, departure, destination, container_ids)
    except Exception as e:
        print(e)
        return []


@router.post("/calculate")
async def calculate(request: CalculateFormRequest):
    coros = []
    destinationId: str | int
    departureId: str | int

    for destinationId in request.destinationExternalIds:
        for departureId in request.departureExternalIds:
            coros.append(_get_routes(
                api_client,
                request.dispatchDate,
                departureId,
                destinationId,
                request.cargoWeight,
                request.containerType,
            ))

    for destinationId in request.destinationInternalIds:
        for departureId in request.departureInternalIds:
            coros.append(_get_routes(
                aggregators,
                request.dispatchDate,
                departureId,
                destinationId,
                request.cargoWeight,
                request.containerType,
            ))

    result = await asyncio.gather(*coros, return_exceptions=True)
    routes = []
    errors = []

    for coro_result in result:
        if isinstance(coro_result, BaseException):
            errors.append({
                "error_type": str(type(coro_result)),
                "error_text": str(coro_result),
            })
        elif coro_result:
            res = list(coro_result)
            if res:
                routes.extend(res)

    return {
        "errors": errors,
        "routes": routes,
    }
