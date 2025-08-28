from importlib.util import find_spec

from fastapi import FastAPI

from sqlalchemy import select

from .database import database
from .models import PointModel, RailRouteModel
from .models.requests.point import AddPointModelRequest
from .models.requests.route import AddRailRouteRequest

if find_spec("dotenv") is not None:
    from dotenv import load_dotenv

    load_dotenv()

app = FastAPI()


async def exe_q(q):
    """ Rendered query-func to get data from DB """
    async with database.session() as session:
        temp = await session.execute(q)
        return temp.scalars().all()


@app.get("/routes")
async def getRoutes():
    stmt = select(
        RailRouteModel,
    )
    routes = await exe_q(stmt)

    return {
        "status": "OK",
        "routes": routes,
    }


@app.get("/points")
async def getPoints():
    stmt = select(
        PointModel,
    )
    points = await exe_q(stmt)

    return {
        "status": "OK",
        "points": points,
    }


@app.post("/points")
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
        "point_id": new_point.id,
    }


@app.post("/routes")
async def addRoute(route: AddRailRouteRequest):
    new_route = RailRouteModel(
        company_id=route.company_id,
        container_id=route.container_id,
        start_point_id=route.start_point_id,
        end_point_id=route.end_point_id,
        effective_from=route.effective_from,
        effective_to=route.effective_to,
        price=route.price,
        drop=route.drop,
        guard=route.guard,
    )

    async with database.session() as session:
        session.add(new_route)
        session.commit()

    return {
        "status": "OK",
        "route_id": new_route.id,
    }
