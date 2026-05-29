import asyncio
import datetime

from backend_user.api.v2.routes.models.form_requests import CalculateFormRequest
from backend_user.dependencies.auth_context import AuthContext
from module_data_fesco_api_adapter import api_client
from module_data_internal import aggregators


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
        containers,
        container_weight,
        container_type,
    )
    if not container_ids:
        return []
    try:
        return await modul.find_all_paths(date, departure, destination, container_ids)
    except Exception as e:
        print(e)
        return []


async def calculate_routes(request: CalculateFormRequest, auth: AuthContext) -> dict:
    coros = []

    for destination_id in request.destinationExternalIds:
        for departure_id in request.departureExternalIds:
            coros.append(
                _get_routes(
                    api_client,
                    request.dispatchDate,
                    departure_id,
                    destination_id,
                    request.cargoWeight,
                    request.containerType,
                )
            )

    for dest_id in request.destinationInternalIds:
        for dep_id in request.departureInternalIds:
            coros.append(
                _get_routes(
                    aggregators,
                    request.dispatchDate,
                    dep_id,
                    dest_id,
                    request.cargoWeight,
                    request.containerType,
                )
            )

    result = await asyncio.gather(*coros, return_exceptions=True)
    routes = []
    errors = []

    for coro_result in result:
        if isinstance(coro_result, BaseException):
            errors.append(
                {
                    "error_type": str(type(coro_result)),
                    "error_text": str(coro_result),
                }
            )
        elif coro_result:
            res = list(coro_result)
            if res:
                routes.extend(res)

    return {
        "errors": errors,
        "routes": routes,
    }
