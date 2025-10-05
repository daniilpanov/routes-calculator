import re

from fastapi import APIRouter, HTTPException

from back_admin.database import database
from back_admin.models import PointModel
from back_admin.models.requests.point import (
    AddPointModelRequest,
    EditPointRequest,
    FilterPointRequest,
)
from sqlalchemy import delete, func, or_, select, update
from sqlalchemy.exc import IntegrityError

router = APIRouter(prefix="/points", tags=["points-admin"])


async def exe_q(q, return_scalar=False):
    async with database.session() as session:
        temp = await session.execute(q)
        return temp.scalar() if return_scalar else temp.scalars().all()


def is_cyrillic(text: str) -> bool:
    return bool(re.search('[а-яА-Я]', text))


@router.post("/find_name")
async def findPoint(search_txt: str):
    stmt = select(
        PointModel,
    )

    if is_cyrillic(search_txt):
        stmt = stmt.where(
            or_(
                PointModel.RU_city.ilike(f"%{search_txt}%"),
                PointModel.RU_country.ilike(f"%{search_txt}%"),
            )
        )
    else:
        stmt = stmt.where(
            or_(
                PointModel.city.ilike(f"%{search_txt}%"),
                PointModel.country.ilike(f"%{search_txt}%"),
            )
        )

    point_name: str = await exe_q(stmt)

    return {
        "status": "OK",
        "point_name": point_name,
    }


@router.post("")
async def getPoints(_filter: FilterPointRequest):
    offset = (_filter.page - 1) * _filter.limit

    stmt = select(PointModel)
    points = await exe_q(stmt)

    result = [
        p
        for p in points
    ]
    total_count: int = len(result)
    result = result[offset: offset + _filter.limit]

    return {
        "status": "OK",
        "count": total_count,
        "points": result,
    }


@router.put("/edit")
async def editPoint(edit_point: EditPointRequest):
    point_stmt = update(
        PointModel,
    ).where(
        PointModel.id == edit_point.point_id,
    )

    update_values = {}
    fields_to_check = ['RU_city', 'RU_country', 'city', 'country']

    for field in fields_to_check:
        value = getattr(edit_point, field, None)
        if value:
            update_values[field] = value

    if update_values:
        point_stmt = point_stmt.values(**update_values)

    async with database.session() as session:
        await session.execute(point_stmt)

        temp = await session.execute(
            select(
                PointModel,
            ).where(
                PointModel.id == edit_point.point_id,
            )
        )
        point_to_change = temp.scalar()

    return {
        "status": "OK",
        "point": point_to_change,
    }


@router.post("/add")
async def addPoint(point: AddPointModelRequest):
    try:
        async with database.session() as session:
            new_point = PointModel(
                city=point.city,
                country=point.country,
                RU_city=point.RU_city,
                RU_country=point.RU_country,
            )
            session.add(new_point)

    except IntegrityError:
        raise HTTPException(
            status_code=400,
            detail="Already exist."
        )

    return {
        "status": "OK",
        "new_point": new_point,
    }


@router.delete("/delete")
async def deletePoints(points_id: list[int]):
    points_delete_stmt = delete(
        PointModel,
    ).where(
        PointModel.id.in_(points_id),
    )

    points_count_stmt = select(
        func.count(PointModel.id),
    ).where(
        PointModel.id.in_(points_id),
    )
    removed_count = await exe_q(points_count_stmt, True)

    async with database.session() as session:
        try:
            await session.execute(points_delete_stmt)
        except IntegrityError:
            raise HTTPException(
                status_code=403,
                detail="Cannot delete point which is already in some routes",
            )

    return {
        "status": "OK",
        "removed_count": removed_count,
    }
