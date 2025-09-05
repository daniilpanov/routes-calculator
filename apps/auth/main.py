import datetime
from contextlib import suppress
from functools import partial

from fastapi import Depends, FastAPI, HTTPException, Response
from starlette.requests import Request
from starlette.responses import JSONResponse

import bcrypt
from fastapi_another_jwt_auth import AuthJWT
from fastapi_another_jwt_auth.exceptions import AuthJWTException
from pydantic import BaseModel
from sqlalchemy import delete, or_, select
from sqlalchemy.orm import joinedload

from .database import database
from .models import CompanyModel, ContainerModel, PointModel, RailRouteModel, SeaRouteModel
from .models.requests.point import AddPointModelRequest
from .models.requests.route import AddRouteRequest, FilterRoutesRequest, RailPrices
from .settings import settings

app = FastAPI()


class User(BaseModel):
    login: str
    password: str


@AuthJWT.load_config
def get_config():
    return settings


@app.exception_handler(AuthJWTException)
def authjwt_exception_handler(request: Request, exc: AuthJWTException):
    return JSONResponse(status_code=exc.status_code, content={"detail": exc.message})


@app.post("/login")
def login(user: User, Authorize: AuthJWT = Depends()):
    admin_pass_bytes = settings.admin_password.encode("utf-8")
    user_pass_bytes = user.password.encode("utf-8")
    admin_password_hash = bcrypt.hashpw(admin_pass_bytes, bcrypt.gensalt())

    is_valid_login = user.login == settings.admin_login
    is_valid_password = bcrypt.checkpw(user_pass_bytes, admin_password_hash)

    if not is_valid_login or not is_valid_password:
        raise HTTPException(
            status_code=401,
            detail="Incorrect login or password"
        )

    access_token = Authorize.create_access_token(subject=user.login)
    refresh_token = Authorize.create_refresh_token(subject=user.login)

    Authorize.set_access_cookies(access_token)
    Authorize.set_refresh_cookies(refresh_token)

    return {"status": "OK"}


@app.post("/token/refresh")
def refresh(Authorize: AuthJWT = Depends()):
    Authorize.jwt_refresh_token_required()
    current_user = Authorize.get_jwt_subject()
    new_access_token = Authorize.create_access_token(subject=current_user)
    Authorize.set_access_cookies(new_access_token)
    return {"status": "OK"}


@app.delete("/logout")
def logout(Authorize: AuthJWT = Depends(), response: Response = None):
    with suppress(Exception):
        Authorize.jwt_required()
    Authorize.unset_jwt_cookies(response=response)
    return {"status": "OK"}


@app.get("/hello")
def hello(Authorize: AuthJWT = Depends()):
    Authorize.jwt_required()
    current_user = Authorize.get_jwt_subject()
    return {"message": f"Hi, {current_user}"}


async def exe_q(q, return_scalar=False):
    async with database.session() as session:
        temp = await session.execute(q)
        return temp.scalar() if return_scalar else temp.scalars().all()


def parseRoute(route, _type):
    res = {
        "route_type": _type,
        "id": route.id,
        "company_id": route.company_id,
        "container_id": route.container_id,
        "start_point_id": route.start_point_id,
        "end_point_id": route.end_point_id,
        "company": route.company,
        "container": route.container,
        "start_point": route.start_point,
        "end_point": route.end_point,
        "effective_from": route.effective_from,
        "effective_to": route.effective_to,
        "price": [
            {
                "type": "filo",
                "value": getattr(route, "filo", None),
                "currency": "USD",
            },
            {
                "type": "fifo",
                "value": getattr(route, "fifo", None),
                "currency": "USD",
            },
            {
                "type": "drop",
                "value": getattr(route, "drop", None),
                "currency": "USD",
            },
            {
                "type": "price",
                "value": getattr(route, "price", None) if not hasattr(route, "filo") else None,
                "currency": "RUB",
            },
            {
                "type": "guard",
                "value": getattr(route, "guard", None),
                "currency": "USD",
            },],
    }
    return res


@app.post("/routes")
async def getRoutes(_filter: FilterRoutesRequest):
    async def getPointIdAndColumn(which_point, name):
        country, city = name.split(", ")
        stmt = select(
            PointModel.id,
        ).where(
            PointModel.RU_country == country,
            PointModel.RU_city == city,
        )

        data = await exe_q(stmt)
        return data, which_point

    async def getCompanyIdAndColumn(name):
        stmt = select(
            CompanyModel.id,
        ).where(
            CompanyModel.name == name,
        )

        data = await exe_q(stmt, True)
        return data, "company_id"

    async def getContainerIdAndColumn(name):
        stmt = select(
            ContainerModel.id,
        ).where(
            ContainerModel.name == name,
        )

        data = await exe_q(stmt, True)
        return data, "container_id"

    offset = (_filter.page - 1) * _filter.limit

    rail_stmt = select(
        RailRouteModel,
    ).options(
        joinedload(RailRouteModel.container),
        joinedload(RailRouteModel.company),
        joinedload(RailRouteModel.start_point),
        joinedload(RailRouteModel.end_point),
    )

    sea_stmt = select(
        SeaRouteModel,
    ).options(
        joinedload(SeaRouteModel.container),
        joinedload(SeaRouteModel.company),
        joinedload(SeaRouteModel.start_point),
        joinedload(SeaRouteModel.end_point),
    )

    keys_map = {
        "start_point": partial(getPointIdAndColumn, "start_point_id"),
        "end_point": partial(getPointIdAndColumn, "end_point_id"),
        "company": getCompanyIdAndColumn,
        "container": getContainerIdAndColumn,
        "effective_from": None,
        "effective_to": None,
    }

    for column, value in _filter.filter_fields:
        if not value:
            continue

        if keys_map[column]:
            value, column = await keys_map[column](value)

        rail_stmt = rail_stmt.where(
            getattr(RailRouteModel, column) == value,
        )

        sea_stmt = sea_stmt.where(
            getattr(SeaRouteModel, column) == value,
        )

    rail_rows = await exe_q(rail_stmt)
    sea_rows = await exe_q(sea_stmt)

    all_rows = [
        parseRoute(row, _type="rail" if isinstance(row, RailRouteModel) else "sea")
        for row in rail_rows + sea_rows
    ]

    paginated_rows = all_rows[offset: offset + _filter.limit]
    total_count = len(rail_rows) + len(sea_rows)

    return {
        "status": "OK",
        "count": total_count,
        "routes": paginated_rows,
    }


@app.post("/routes/add")
async def addRoute(route: AddRouteRequest):
    date_from = datetime.datetime.strptime(route.effective_from, "%d.%m.%Y").date()
    date_to = datetime.datetime.strptime(route.effective_to, "%d.%m.%Y").date()

    if date_from >= date_to:
        raise HTTPException(
            status_code=400,
            detail=f"Dates '{route.effective_from} - {route.effective_to}' invalid"
        )

    start_country, start_city = route.start_point_name.split(", ")
    end_country, end_city = route.end_point_name.split(", ")

    # Start point parse
    start_point_stmt = select(
        PointModel,
    ).where(
        PointModel.RU_country == start_country,
        PointModel.RU_city == start_city,
    )
    start_point = await exe_q(start_point_stmt, True)

    if not start_point:
        raise HTTPException(
            status_code=404,
            detail=f"Start point '{route.start_point_name}' not found"
        )

    # End point parse
    end_point_stmt = select(
        PointModel,
    ).where(
        PointModel.RU_country == end_country,
        PointModel.RU_city == end_city,
    )
    end_point = await exe_q(end_point_stmt, True)

    if not end_point:
        raise HTTPException(
            status_code=404,
            detail=f"End point '{route.end_point_name}' not found"
        )

    # Company parse
    company_stmt = select(
        CompanyModel,
    ).where(
        CompanyModel.name == route.company,
    )
    company = await exe_q(company_stmt, True)

    if not company:
        raise HTTPException(
            status_code=404,
            detail=f"Company '{route.company}' not found"
        )

    # Container parse
    container_stmt = select(
        ContainerModel,
    ).where(
        ContainerModel.name == route.container,
    )
    container = await exe_q(container_stmt, True)

    if not container:
        raise HTTPException(
            status_code=404,
            detail=f"Container '{route.container}' not found"
        )

    if getattr(route.price, "drop", None):
        new_route = RailRouteModel(
            company=company,
            container=container,
            start_point=start_point,
            end_point=end_point,
            effective_from=date_from,
            effective_to=date_to,
            price=route.price.price,
            drop=route.price.drop,
            guard=route.price.guard,
        )
        route_type = "rail"

    else:
        new_route = SeaRouteModel(
            company=company,
            container=container,
            start_point=start_point,
            end_point=end_point,
            effective_from=date_from,
            effective_to=date_to,
            filo=route.price.filo,
            fifo=route.price.fifo,
        )
        route_type = "sea"


    async with database.session() as session:
        session.add(new_route)
        await session.commit()

    result = parseRoute(new_route, _type=route_type)

    return {
        "status": "OK",
        "new_route": result,
    }


@app.delete("/routes/delete")
async def deleteRoute(route_id: int):
    stmt = select(
        RailRouteModel,
    ).where(
        RailRouteModel.id == route_id,
    )

    route = await exe_q(stmt, True)
    if not route:
        return {
            "status": f"Not found '{route_id}'"
        }

    async with database.session() as session:
        await session.delete(route)
        session.commit()

    return {
        "status": "OK",
        "route_id": route_id,
    }


@app.post("/point/find_name")
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


@app.post("/points")
async def getPoints():
    stmt = select(PointModel)
    points = await exe_q(stmt)

    return {
        "status": "OK",
        "points": points,
    }


@app.post("/points/add")
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


@app.delete("/points/delete")
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
