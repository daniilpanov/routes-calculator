from ..models.point import LangType
from .containers import _map_container


def _map_segment(
    route, price, currency, _type, services, begin_cond=None, finish_cond=None
):
    start_point_RU_city = (a.alias_name
                           for a in route.start_point.aliases
                           if a.lang == LangType.RU and a.is_main == 1)
    end_point_RU_city = (a.alias_name
                         for a in route.end_point.aliases
                         if a.lang == LangType.RU and a.is_main == 1)

    item = {
        "company": route.company.name,
        "type": _type,
        "effectiveFrom": route.effective_from,
        "effectiveTo": route.effective_to,
        "startPointCountry": route.start_point.RU_country,
        "startPointName": start_point_RU_city,
        "endPointCountry": route.end_point.RU_country,
        "endPointName": end_point_RU_city,
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


def _map_route(routes):
    res = []
    _types = []
    for route in routes:
        if getattr(route, "filo", None):
            _types.append("sea")
            res.append(_map_segment(route, "filo", "USD", "sea", {}, "FI", "LO"))
        elif getattr(route, "fifo", None):
            _types.append("sea")
            res.append(_map_segment(route, "fifo", "USD", "sea", {}, "FI", "FOR"))
        else:
            _types.append("rail")
            res.append(
                _map_segment(
                    route,
                    "price",
                    "RUB",
                    "rail",
                    {
                        "guard": "RUB",
                    },
                )
            )

    extended_routes = []
    for i, _type in reversed(list(enumerate(_types))):
        if _type != "rail":
            break
        extended_routes.append(_map_segment(routes[i], "drop", "USD", "truck", {}))
    else:
        extended_routes = []

    res.extend(extended_routes)
    return res


def map_routes(routes):
    return map(_map_route, routes)
