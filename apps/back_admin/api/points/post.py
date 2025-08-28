from fastapi import APIRouter
from sqlalchemy import select, or_

from back_admin.database import database
from back_admin.models import PointModel
from back_admin.models.requests.point import AddPointModelRequest

router = APIRouter(prefix="/points", tags=["points"])

async def exe_q(q, return_scalar=False):
    async with database.session() as session:
        temp = await session.execute(q)
        return temp.scalar() if return_scalar else temp.scalars().all()

@router.post("/find_name")
async def findPoint(search_txt: str):
    stmt = select(
        PointModel,
    ).where(
        or_(
            PointModel.RU_city.ilike(f"%{search_txt}%"),
            PointModel.RU_country.ilike(f"%{search_txt}%"),
        )
    )
    point_name: str = await exe_q(stmt)

    return {
        "status": "OK",
        "point_name": point_name,
    }


@router.post("")
async def getPoints():
    stmt = select(PointModel)
    points = await exe_q(stmt)

    return {
        "status": "OK",
        "points": points,
    }


@router.post("/add")
async def addPoint(point: AddPointModelRequest):
    new_point = PointModel(
        city=point.city,
        country=point.country,
        RU_city=point.RU_city,
        RU_country=point.RU_country,
    )
    async with database.session() as session:
        session.add(new_point)
        session.commit()

    return {
        "status": "OK",
        "new_point": new_point,
    }


@router.delete("/delete")
async def deletePoint(point_id: int):
    stmt = select(
        PointModel,
    ).where(
        PointModel.id == point_id,
    )
    async with database.session() as session:
        await session.delete(stmt)
        session.commit()

    return {
        "status": "OK",
        "point_id": point_id,
    }
