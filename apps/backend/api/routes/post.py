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

        print(service)
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

    for routes_net in routes:
        initial_company = routes_net[0]["company"]
        for route in routes_net[1:]:
            if route["company"] != initial_company:
                multi_service_routes.append(routes_net)
                break
        else:
            one_service_routes.append(routes_net)

    return {
        "one_service_routes": one_service_routes,
        "multi_service_routes": multi_service_routes,
    }
