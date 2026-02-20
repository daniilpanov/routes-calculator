import asyncio
import datetime
from collections import defaultdict
from typing import Any

from fastapi import APIRouter

from aiohttp import ClientResponseError
from backend.services import custom, fesco

router = APIRouter(prefix="/points", tags=["points"])


def _error_or_data(result):
    return (
        {"success": True, "data": list(result)}
        if not isinstance(result, Exception) else
        {"success": True, "data": []}
        if isinstance(result, ClientResponseError) and result.status == 400 else
        {"success": False, "error": str(result), "type": str(type(result))}
    )


def _group_point_companies(points: list[dict[str, Any]]) -> list[dict[str, Any]]:
    point_companies = defaultdict(list)
    point_info = {}

    for point in points:
        point_id = point["id"]

        if point_id not in point_info:
            point_info[point_id] = {
                "id": point_id,
                "ports": point["ports"].copy() if "ports" in point else [],
                "translates": point["translates"].copy() if "translates" in point else {}
            }

        point_companies[point_id].append(point["company"])

    result = []
    for point_id, companies in point_companies.items():
        grouped_point = point_info[point_id].copy()
        grouped_point["companies"] = companies
        result.append(grouped_point)

    return result


@router.get("/")
async def all_points():
    fesco_points, custom_points = await asyncio.gather(
        fesco.get_all_points(),
        custom.get_all_points(),
        return_exceptions=True,
    )

    errors = {}
    points = []

    if isinstance(fesco_points, Exception):
        errors["external"] = {
            "error_text": str(fesco_points),
            "error_type": str(type(fesco_points)),
        }
    else:
        points.extend(fesco_points)

    if isinstance(custom_points, Exception):
        errors["internal"] = {
            "error_text": str(custom_points),
            "error_type": str(type(custom_points)),
        }
    else:
        points.extend(custom_points)

    return {
        "errors": errors,
        "data": _group_point_companies(points),
    }


@router.get("/departures")
async def all_departure_by_date(date: datetime.date):
    fesco_departures, custom_departures = map(_error_or_data, await asyncio.gather(
        fesco.get_departure_points_by_date(date),
        custom.get_departure_points(),
        return_exceptions=True,
    ))

    return {
        "external": fesco_departures,
        "internal": custom_departures,
    }


@router.get("/destinations")
async def all_destination_by_date(date: datetime.date, external_point_id: str | None = None):
    coros = [custom.get_departure_points()]
    if external_point_id:
        coros.append(fesco.get_destination_points_by_date(date, external_point_id))

    departures = list(
        map(
            _error_or_data,
            await asyncio.gather(
                *coros,
                return_exceptions=True,
            ),
        ),
    )

    return {
        "external": departures[1] if len(departures) > 1 else {"success": True, "data": []},
        "internal": departures[0],
    }
