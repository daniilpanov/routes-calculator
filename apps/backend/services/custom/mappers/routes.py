from typing import Any

from ..models import DropModel
from .containers import _map_container


def _map_segment(
    route, price, currency, _type, services, begin_cond=None, finish_cond=None
):
    item = {
        "company": route.company.name,
        "type": _type,
        "effectiveFrom": route.effective_from,
        "effectiveTo": route.effective_to,
        "startPointCountry": route.start_point.RU_country,
        "startPointName": route.start_point.RU_city,
        "endPointCountry": route.end_point.RU_country,
        "endPointName": route.end_point.RU_city,
        "container": _map_container(route.container),
        "price": getattr(route, price),
        "currency": currency,
        "services": {
            k: {"price": getattr(route, k), "currency": c} for k, c in services.items()
        },
    }
    if begin_cond is not None:
        item.update(
            {
                "beginCond": begin_cond,
                "finishCond": finish_cond,
            }
        )
    return item


def _map_route(route_and_drop):
    segments = route_and_drop
    drop = None
    if isinstance(segments[-1], DropModel) or not segments[-1]:
        drop = segments[-1]
        segments = segments[:-1]

    res: list[Any] = [None] * len(segments)
    _types: list[str | None] = [None] * len(segments)

    for i, segment in enumerate(segments):
        if getattr(segment, "filo", None):
            _types[i] = "sea"
            res[i] = _map_segment(segment, "filo", "USD", "sea", {}, "FI", "LO")
        elif getattr(segment, "fifo", None):
            _types[i] = "sea"
            res[i] = _map_segment(segment, "fifo", "USD", "sea", {}, "FI", "FOR")
        else:
            _types[i] = "rail"
            res[i] = (
                _map_segment(
                    segment,
                    "price",
                    "RUB",
                    "rail",
                    {"guard": "RUB"},
                )
            )

    return (res, {"price": drop.price, "currency": drop.currency}) if drop else (res, None)


def map_routes(routes_and_drops):
    return map(_map_route, routes_and_drops)
