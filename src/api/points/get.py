import datetime
import json
from functools import lru_cache

from fastapi import APIRouter

from src.services import custom, fesco
from src.utils.string_formatters import union_country_and_name

router = APIRouter(prefix="/points", tags=["points"])


async def _add_data(main_dict, data):
    try:
        items = await data
    except Exception as e:
        print(e)
        return e
    for full_name, service, _id in (
        (
            union_country_and_name(main_dict, x.get("country"), x.get("name")),
            x["company"],
            x["id"],
        )
        for x in items
    ):
        main_dict.setdefault(full_name, {})[service] = _id


@lru_cache(1024)
@router.get("/departures")
async def all_departure_by_date(date: datetime.date):
    prepared_from: dict[str, dict] = {}
    # from FESCO
    await _add_data(prepared_from, fesco.get_departure_points_by_date(date))
    # from CUSTOM
    await _add_data(prepared_from, custom.get_departure_points_by_date(date))

    result = {}
    for loc, data in prepared_from.items():
        result[f"{loc} [" + (", ".join(service for service in data)) + "]"] = data

    return result


@lru_cache(1024)
@router.get("/destinations")
async def all_destination_by_date(date: datetime.date, departure_point_id: str):
    departure_ids = json.loads(departure_point_id)
    prepared_to: dict[str, dict] = {}
    # from FESCO
    if "FESCO" in departure_ids:
        await _add_data(
            prepared_to,
            fesco.get_destination_points_by_date(date, departure_ids.pop("FESCO")),
        )
    # from CUSTOM
    for _id in departure_ids.values():
        await _add_data(prepared_to, custom.get_destination_points_by_date(date, _id))

    result = {}
    for loc, data in prepared_to.items():
        result[f"{loc} [" + (", ".join(service for service in data)) + "]"] = data

    return result
