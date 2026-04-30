from .containers import _map_container

_segment_types = {
    1: "rail",
    2: "sea",
    3: "truck",
}


def _check_currency(currency):
    return "RUB" if currency == "RUR" else currency


def _map_segment(segment):
    return {
        "id": segment["SegmentUID"],
        "type": _segment_types.get(segment["SegmentType"]),
        "startPointCountry": segment["BeginCountryName"],
        "startPointName": segment["BeginLocName"],
        "endPointCountry": segment["FinishCountryName"],
        "endPointName": segment["FinishLocName"],
        "price": segment["Containers"][0]["Price"],
        "currency": _check_currency(segment["Containers"][0]["Currency"]),
    }


def _map_service(service):
    if service.get("group"):
        service = service["items"][0]

    return {
        "segment_id": service["SegmentUID"],
        "name": service["ServiceType"][0]["ServiceTypeName"] if service["ServiceType"] else service["ServiceName"],
        "description": service["ServiceName"],
        "hint": service["ServiceComment"] or None,
        "checked": service["checked"],
        "mandatory": service["Default"] and service["InclMainServicePrice"],
        "currency": service["ContPrice"][0]["Currency"] if service["ContPrice"] else None,
        "price": (
            service["ContPrice"][0]["Price"] * service["ContPrice"][0]["Quantity"] if service["ContPrice"] else None
        ),
    }


def _map_route(route):
    services = list(map(_map_service, route.get("Services", [])))

    res = []
    for segm in map(_map_segment, route.get("Segments", [])):
        item = {
            "company": "FESCO",
            "effectiveFrom": route["DateFrom"],
            "effectiveTo": route["DateTo"],
            "container": _map_container(route["Containers"][0]),
            "services": {},
        }
        item.update(segm)
        if segm["type"] == "sea":
            item.update(
                {
                    "beginCond": route["BeginCond"],
                    "finishCond": route["FinishCond"],
                }
            )
        res.append(item)
    return res, None, False, services


def map_routes(routes):
    return map(_map_route, routes)
