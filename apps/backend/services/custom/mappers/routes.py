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
    *segments, drop = route_and_drop
    res = []
    _types = []

    for segment in segments:
        if getattr(segment, "filo", None):
            _types.append("sea")
            res.append(_map_segment(segment, "filo", "USD", "sea", {}, "FI", "LO"))
        elif getattr(segment, "fifo", None):
            _types.append("sea")
            res.append(_map_segment(segment, "fifo", "USD", "sea", {}, "FI", "FOR"))
        else:
            _types.append("rail")
            res.append(
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
