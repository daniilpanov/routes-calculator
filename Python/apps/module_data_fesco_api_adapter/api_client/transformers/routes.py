from .containers import transform_container

_segment_types = {
    1: "rail",
    2: "sea",
    3: "truck",
}


def _check_currency(currency):
    return "RUB" if currency == "RUR" else currency


def transform_segment(segment, container, date_from, date_to, container_transfer_terms):
    return {
        "id": segment["SegmentUID"],
        "type": _segment_types.get(segment["SegmentType"]),
        "company": "FESCO",
        "effectiveFrom": date_from,
        "effectiveTo": date_to,
        "container_transfer_terms": container_transfer_terms,
        "container_owner": "COC",
        "startPointCountry": segment["BeginCountryName"],
        "startPointName": segment["BeginLocName"],
        "endPointCountry": segment["FinishCountryName"],
        "endPointName": segment["FinishLocName"],
        "services": {},
        "prices": [{
            "conversation_percents": 0.0,
            "currency": _check_currency(segment["Containers"][0]["Currency"]),
            "value": segment["Containers"][0]["Price"],
            "container": container,
        }],
    }


def transform_service(service):
    if service.get("group"):
        if not service.get("items") or not len(service["items"]):
            print(f"WARNING\tError in parsing FESCO service group: {service}")
            return None

        service = service["items"][0]

    mandatory_keys = {"SegmentUID", "ServiceName", }
    for key in mandatory_keys:
        if key not in service:
            print(f"WARNING\tError in parsing FESCO service: {service}")
            return None

    return {
        "segment_id": service["SegmentUID"],
        "name": service["ServiceType"][0]["ServiceTypeName"] if service["ServiceType"] else service["ServiceName"],
        "description": service["ServiceName"],
        "hint": service.get("ServiceComment") or None,
        "checked": service.get("checked", False),
        "mandatory": service.get("Default", False) and service.get("InclMainServicePrice", False),
        "currency": service["ContPrice"][0]["Currency"] if service["ContPrice"] else None,
        "price": (
            service["ContPrice"][0]["Price"] * service["ContPrice"][0]["Quantity"] if service["ContPrice"] else None
        ),
    }


def transform_route(route):
    services = [item for item in map(transform_service, route.get("Services", [])) if item]
    container_descriptor = transform_container(route["Containers"][0])

    return (
        [
            transform_segment(
                seg,
                container_descriptor,
                route["DateFrom"],
                route["DateTo"],
                route["BeginCond"] + route["FinishCond"],
            ) for seg in route.get("Segments", [])
        ],
        None,
        False,
        services,
    )


def transform_routes(routes):
    return map(transform_route, routes)
