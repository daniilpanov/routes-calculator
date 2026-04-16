import asyncio
import datetime
from collections.abc import Iterator
from typing import Annotated, Any

from fastapi import APIRouter, HTTPException
from fastapi.params import Depends, Query
from starlette.status import HTTP_500_INTERNAL_SERVER_ERROR

from aiohttp import ClientResponseError
from backend_user.services import custom, fesco
from backend_user.services.custom.mappers.points import map_points_v2 as map_custom
from backend_user.services.fesco.mappers.points import map_points_v2 as map_fesco
from backend_user.utils.group_points import group_companies, group_transfers, raw_point_from_dict
from module_shared.models import CompanyModel, PointModel

router = APIRouter(prefix="/v2/points", tags=["v2", "points"])


def _error_or_data(result):
    return (
        {"success": True, "data": list(result)}
        if not isinstance(result, BaseException) else
        {"success": True, "data": []}
        if isinstance(result, ClientResponseError) and result.status == 400 else
        {"success": False, "error": str(result), "type": str(type(result))}
    )


def _parse_point_ids(departure_point_ids: Annotated[str, Query]) -> tuple[list[int], list[str]]:
    if not departure_point_ids:
        return [], []

    internal_point_ids: list[int] = []
    external_point_ids: list[str] = []
    for encoded_point_id in departure_point_ids.split(","):
        if encoded_point_id[0] == "E":
            external_point_ids.append(encoded_point_id[1:])
        else:
            internal_point_ids.append(int(encoded_point_id[1:]))

    return internal_point_ids, external_point_ids


@router.get("/departures")
async def all_departure_by_date(date: datetime.date):
    fesco_points: Iterator[dict[str, Any]]
    custom_points: list[tuple[PointModel, CompanyModel]]

    fesco_points, custom_points = await asyncio.gather(
        fesco.get_departure_points_by_date(date),
        custom.get_departure_points(),
        return_exceptions=True,
    )

    errors = []
    data: list[dict[str, Any]] = []

    if isinstance(fesco_points, BaseException):
        errors.append({
            "source": "external",
            "error_text": str(fesco_points),
            "error_type": str(type(fesco_points)),
        })
    else:
        data.extend(map_fesco(fesco_points))

    if isinstance(custom_points, BaseException):
        errors.append({
            "source": "internal",
            "error_text": str(custom_points),
            "error_type": str(type(custom_points)),
        })
    else:
        data.extend(map_custom(custom_points))

    return {
        "errors": errors,
        "data": group_transfers(group_companies([raw_point_from_dict(point) for point in data], {"FESCO"}), {"FESCO"}),
    }


@router.get("/destinations")
async def all_destination_by_date(
    date: datetime.date,
    departure_point_ids: Annotated[tuple[list[int], list[str]], Depends(_parse_point_ids)],
):
    coros = [custom.get_destination_points()]

    _, external_point_ids = departure_point_ids

    for point_id in external_point_ids:
        coros.append(fesco.get_destination_points_by_date(date, point_id))

    results = await asyncio.gather(
        *coros,
        return_exceptions=True,
    )

    errors = []
    data = []

    if not results:
        raise HTTPException(HTTP_500_INTERNAL_SERVER_ERROR, detail="Unknown error: no results")

    fesco_points_array: list[Iterator[dict[str, Any]] | BaseException]
    custom_points, *fesco_points_array = results
    if isinstance(custom_points, BaseException):
        errors.append({
            "source": "internal",
            "error_text": str(custom_points),
            "error_type": str(type(custom_points)),
        })
    else:
        data.extend(map_custom(custom_points))

    for fesco_points in fesco_points_array:
        if isinstance(fesco_points, BaseException):
            errors.append({
                "source": "external",
                "error_text": str(fesco_points),
                "error_type": str(type(fesco_points)),
            })
        else:
            data.extend(map_fesco(fesco_points))

    return {
        "errors": errors,
        "data": group_transfers(group_companies([raw_point_from_dict(point) for point in data], {"FESCO"}), {"FESCO"}),
    }
