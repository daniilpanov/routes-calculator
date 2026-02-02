from fastapi import APIRouter

from backend.services import custom, fesco

from .models.form_requests import CalculateFormRequest

router = APIRouter(prefix="/routes", tags=["routes"])


async def _get_routes(
    modul,
    date,
    departure,
    destination,
    container_weight,
    container_type,
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
async def calculate(request: CalculateFormRequest):
    routes = []

    if "FESCO" in request.destinationId:
        routes.extend(
            await _get_routes(
                fesco,
                request.dispatchDate,
                request.departureId.pop("FESCO"),
                request.destinationId.pop("FESCO"),
                request.cargoWeight,
                request.containerType,
            )
        )

    points = set()
    for service in request.destinationId:
        if service in request.departureId:
            points.add((request.departureId[service], request.destinationId[service]))

    for departureId, destinationId in points:
        routes.extend(
            await _get_routes(
                custom,
                request.dispatchDate,
                departureId,
                destinationId,
                request.cargoWeight,
                request.containerType,
                request.onlyInSelectedDateRange,
            )
        )

    one_service_routes = []
    multi_service_routes = []

    for route_and_drop_and_datecheck in routes:
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
        "one_service_routes": one_service_routes,
        "multi_service_routes": multi_service_routes,
    }
