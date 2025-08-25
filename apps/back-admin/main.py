import asyncio
from importlib.util import find_spec

from fastapi import FastAPI
from fastapi.encoders import jsonable_encoder
from starlette.responses import JSONResponse

from backend.mapper_decorator import apply_mapper
from backend.services.custom.mappers.routes import map_routes
from backend.services.custom.models import PointModel, RailRouteModel
from backend.services.custom.routes import _execute_query
from sqlalchemy import insert, select
from sqlalchemy.orm import aliased, joinedload

if find_spec("dotenv") is not None:
    from dotenv import load_dotenv

    load_dotenv()

app = FastAPI(
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json"
)


def parse_routes_to_js(_routes):
    return jsonable_encoder({
        "status": "OK",
        "routes": list(_routes)
    })


async def exe_q(queries):
    """ Rendered func to execute list of sql-queries """
    coroutines = [_execute_query(query) for query in queries]
    results = await asyncio.gather(*coroutines, return_exceptions=True)
    flat_result: list[dict] = []

    for r in results:
        if r and not isinstance(r, BaseException):
            flat_result.extend(r)

    return flat_result


@apply_mapper(map_routes)
async def stmt():
    rail = aliased(RailRouteModel)
    query_rail = (
        select(rail)
        .options(
            joinedload(rail.start_point),
            joinedload(rail.end_point),
            joinedload(rail.company),
            joinedload(rail.container),
        )
    )

    all_queries = [query_rail]
    return exe_q(all_queries)


@app.get("/routes")
async def getRoutes():
    routes = await stmt()

    return JSONResponse(
        content=parse_routes_to_js(routes),
        status_code=200
    )


@app.post("/points")
async def addPoint(point: PointModel):
    point_query = (
        insert(PointModel)
        .values(
            id=point.id,
            city=point.city,
            country=point.country,
            RU_city=point.RU_city,
            RU_country=point.RU_country
        )
    )

    all_queries = [
        point_query,
    ]

    return {"status": "OK",
            "result": exe_q(all_queries)}


@app.post("/routes")
async def addRoute(route: RailRouteModel):
    routeClass = aliased(RailRouteModel)
    route_query = (
        insert(routeClass)
        .values(
            id=route.id,
            company_id=route.company_id,
            container_id=route.container_id,
            start_point_id=route.start_point_id,
            end_point_id=route.end_point_id,
            effective_from=route.effective_from,
            effective_to=route.effective_to,
            price=route.price,
            drop=route.drop,
            guard=route.guard
        )
    )

    all_queries = [
        route_query,
    ]

    return {"status": "OK",
            "result": exe_q(all_queries)}
