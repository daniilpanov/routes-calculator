from typing import Any

from module_data_internal.schemas import DropModel, RouteModel
from module_shared.database import Base

from .containers import _map_container


def _map_segment(route: RouteModel):
    return {
        "id": route.id,
        "company": route.company.name,
        "type": route.type.name,
        "effectiveFrom": route.effective_from,
        "effectiveTo": route.effective_to,
        "startPointCountry": route.start_point.RU_country,
        "startPointName": route.start_point.RU_city,
        "endPointCountry": route.end_point.RU_country,
        "endPointName": route.end_point.RU_city,
        "comment": route.comment,

        "container_transfer_terms": route.container_transfer_terms,
        "container_shipment_terms": route.container_shipment_terms,
        "container_owner": route.container_owner,

        "prices": [{
            "container": _map_container(price.container),
            "value": price.value,
            "currency": price.currency,
            "conversation_percents": price.conversation_percents,
        } for price in route.prices],

        "services": [{
            "name": service.service.name,
            "description": service.service.description,
            "hint": service.service.hint,
            "currency": service.currency,
            "price": service.price,
            "checked": service.service.default,
            "mandatory": service.service.mandatory,
        } for service in route.services],
    }


def _map_route(route_and_drop_and_datecheck: tuple[list[Base], bool]):
    segments, may_route_be_invalid = route_and_drop_and_datecheck
    drop: DropModel | None = None
    if isinstance(segments[-1], DropModel) or not segments[-1]:
        drop = segments[-1]
        segments = segments[:-1]

    mapped_segments = [None] * len(segments)
    services: list[dict[str, Any]] = []

    for i, segment in enumerate(map(_map_segment, segments)):
        services.extend({"segment_id": segment["id"], **service} for service in segment["services"])
        del segment["services"]
        mapped_segments[i] = segment

    return (
        mapped_segments,
        {
            "price": drop.price,
            "conversation_percents": drop.conversation_percents,
            "currency": drop.currency,
        } if drop else None,
        may_route_be_invalid,
        services,
    )


def map_routes(routes_and_drops_and_datecheck: list[tuple[list[Base], bool]]):
    return map(_map_route, routes_and_drops_and_datecheck)
