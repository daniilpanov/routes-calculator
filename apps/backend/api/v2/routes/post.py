import asyncio
import datetime

from fastapi import APIRouter

from backend.services import custom, fesco

from .models.form_requests import CalculateFormRequest

router = APIRouter(prefix="/v2/routes", tags=["v2", "routes"])


async def _get_routes(
    modul,
    date: datetime.date,
    departure: str | int,
    destination: str | int,
    container_weight: float,
    container_type: int,
    only_in_selected_date_range: bool = False,
):
    containers = await modul.get_containers(date, departure, destination)
    container_ids = modul.search_container_ids(
        containers, container_weight, container_type
    )
    if not container_ids:
        return []
    try:
        return await modul.find_all_paths(date, departure, destination, container_ids, only_in_selected_date_range)
    except Exception as e:
        print(e)
        return []


@router.post("/calculate")
async def calculate(request: CalculateFormRequest):  # noqa: C901
    coros = []
    destinationId: str | int
    departureId: str | int

    for destinationId in request.destinationExternalIds:
        for departureId in request.departureExternalIds:
            coros.append(_get_routes(
                fesco,
                request.dispatchDate,
                departureId,
                destinationId,
                request.cargoWeight,
                request.containerType,
            ))

    for destinationId in request.destinationInternalIds:
        for departureId in request.departureInternalIds:
            coros.append(_get_routes(
                custom,
                request.dispatchDate,
                departureId,
                destinationId,
                request.cargoWeight,
                request.containerType,
                request.onlyInSelectedDateRange,
            ))

    result = await asyncio.gather(*coros, return_exceptions=True)
    errors = []
    one_service_routes = []
    multi_service_routes = []

    for coro_result in result:
        if isinstance(coro_result, BaseException):
            errors.append({
                "error_type": str(type(coro_result)),
                "error_text": str(coro_result),
            })
            continue

        for route_and_drop_and_datecheck in coro_result:
            if len(route_and_drop_and_datecheck) == 3:
                route, drop, may_route_be_invalid = route_and_drop_and_datecheck
            else:  # magic fallback
                route = route_and_drop_and_datecheck[0]
                drop = None
                may_route_be_invalid = False

            initial_company = route[0]["company"]
            for segment in route[1:]:
                if segment["company"] != initial_company:
                    multi_service_routes.append((route, drop, may_route_be_invalid))
                    break
            else:
                one_service_routes.append((route, drop, may_route_be_invalid))

    return {
        "errors": errors,
        "one_service_routes": one_service_routes,
        "multi_service_routes": multi_service_routes,
    }
