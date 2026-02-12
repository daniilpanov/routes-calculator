from typing import Any

from backend.database import Base

from ..models import DropModel
from .containers import _map_container


def _map_segment(route):
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
        "prices": [{
            "container": _map_container(price.container),
            "value": price.value,
            "currency": price.currency,
            "conversation_percents": price.conversation_percents,
            "cond": price.type,
        } for price in route.prices],
    }


def _map_route(route_and_drop: list[Base]):
    segments = route_and_drop
    drop: DropModel | None = None
    if isinstance(segments[-1], DropModel) or not segments[-1]:
        drop = segments[-1]
        segments = segments[:-1]

    res: list[Any] = [None] * len(segments)
    skipped_count = 0

    for i, segment in enumerate(segments):
        mapped_segment = _map_segment(segment)
        if mapped_segment:
            res[i - skipped_count] = mapped_segment
        else:
            skipped_count += 1

    return (res, {"price": drop.price, "currency": drop.currency}) if drop else (res, None)


def map_routes(routes_and_drops: list[list[Base]]):
    return map(_map_route, routes_and_drops)
