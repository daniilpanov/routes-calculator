from typing import Any

from module_shared.database import Base
from module_shared.models import DropModel, RouteModel

from .containers import _map_container


def _map_segment(route: RouteModel):
    return {
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
    }


def _map_route(route_and_drop_and_datecheck: tuple[list[Base], bool]):
    segments, may_route_be_invalid = route_and_drop_and_datecheck
    drop: DropModel | None = None
    if isinstance(segments[-1], DropModel) or not segments[-1]:
        drop = segments[-1]
        segments = segments[:-1]

    mapped_segments = list(map(_map_segment, segments))

    return (
        mapped_segments,
        {
            "price": drop.price,
            "conversation_percents": drop.conversation_percents,
            "currency": drop.currency,
        } if drop else None,
        may_route_be_invalid,
    )


def map_routes(routes_and_drops_and_datecheck: list[tuple[list[Base], bool]]):
    return map(_map_route, routes_and_drops_and_datecheck)
