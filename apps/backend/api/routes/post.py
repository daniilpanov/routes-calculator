from fastapi import APIRouter

from backend.services import custom, fesco

from .models.form_requests import CalculateFormRequest

router = APIRouter(prefix="/routes", tags=["routes"])


async def _get_routes(
    modul, date, departure, destination, container_weight, container_type
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
    for service in request.destinationId:
        if service not in request.departureId:
            continue

        routes.extend(
            await _get_routes(
                custom,
                request.dispatchDate,
                request.departureId[service],
                request.destinationId[service],
                request.cargoWeight,
                request.containerType,
            )
        )

    one_service_routes = []
    multi_service_routes = []
    print(routes)
    for route_and_drop in routes:
        if len(route_and_drop) > 1:
            route, drop = route_and_drop
        else:
            route = route_and_drop[0]
            drop = None
        print(route, drop)
        initial_company = route[0]["company"]
        for segment in route[1:]:
            if segment["company"] != initial_company:
                multi_service_routes.append((route, drop))
                break
        else:
            one_service_routes.append((route, drop))

    return {
        "one_service_routes": one_service_routes,
        "multi_service_routes": multi_service_routes,
    }
