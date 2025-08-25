import asyncio
from importlib.util import find_spec

from fastapi import FastAPI
from fastapi.encoders import jsonable_encoder
from starlette.responses import JSONResponse

from backend.mapper_decorator import apply_mapper
from backend.services.custom.mappers.routes import map_routes
from backend.services.custom.models import RailRouteModel
from backend.services.custom.routes import _execute_query
from sqlalchemy import select
from sqlalchemy.orm import aliased, joinedload

if find_spec("dotenv") is not None:
    from dotenv import load_dotenv

    load_dotenv()


app = FastAPI(
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json"
)


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

    coroutines = [_execute_query(query) for query in all_queries]
    results = await asyncio.gather(*coroutines, return_exceptions=True)
    flat_result: list[dict] = []

    for r in results:
        if r and not isinstance(r, BaseException):
            flat_result.extend(r)

    return flat_result


@app.get("/routes")
async def getRoutes():
    routes = await stmt()
    json_compatible_data = jsonable_encoder({
        "status": "OK",
        "routes": list(routes)
    })

    return JSONResponse(
        content=json_compatible_data,
        status_code=200
    )
