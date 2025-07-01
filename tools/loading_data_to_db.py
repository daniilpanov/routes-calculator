import asyncio

from dotenv import load_dotenv
from sqlalchemy import select

load_dotenv(".env.local") or load_dotenv("../.env.local")

import pandas as pd

from src.database import database
from src.services.custom.models import (
    CompanyModel,
    ContainerModel,
    PointModel,
    RailRouteModel,
    SeaRouteModel,
)


def extract_data(df: pd.DataFrame):
    services = df["Service"].unique()

    points = pd.concat(  # noqa: ECE001
        [
            df[["Service", "POL COUNTRY", "POL FULL NAME"]].rename(
                columns={"POL COUNTRY": "Country", "POL FULL NAME": "City"},
            ),
            df[["Service", "POD COUNTRY", "POD FULL NAME"]].rename(
                columns={"POD COUNTRY": "Country", "POD FULL NAME": "City"},
            ),
        ]
    ).drop_duplicates()

    containers = df[
        ["CONTAINER TYPE", "CONTAINER SIZE", "Container weight limit"]
    ].drop_duplicates()

    return services, points, containers


def create_independent_models(services, points, containers):
    service_models = {}
    point_models = {}
    container_models = {}
    container_typed_models = {}

    for service in services:
        service_models[service] = CompanyModel(name=service)

    for _, point in points.iterrows():
        point_models[(point["Country"], point["City"])] = PointModel(
            country=point["Country"], city=point["City"]
        )

    list_containers = sorted(
        containers.values.tolist(), key=lambda x: x[1] * 100 + x[2]
    )
    _curr_size = None
    _curr_weight = 0

    for _type, _size, _weight_to in list_containers:
        if _curr_size == _size:
            _weight_from = _curr_weight
            _curr_weight = _weight_to
        else:
            _weight_from = 0
            _curr_weight = _weight_to
            _curr_size = _size
        if pd.isna(_weight_to):
            _curr_weight = 0
            continue

        inst = ContainerModel(
            type=_type,
            size=_size,
            weight_from=_weight_from,
            weight_to=_weight_to,
            name=f"{_size}'{_type} ≥{int(_weight_to)}t",
        )
        container_models[(_type, _size, _weight_to)] = inst
        container_typed_models.setdefault((_type, _size), []).append(inst)

    return service_models, point_models, container_models, container_typed_models


def create_routes(
    df, model_type, price_fields, filter_fields, services, points, containers
):
    models = []
    for _, route in df.iterrows():
        _skip = False
        for ff in filter_fields:
            f = route.get(ff)
            if f and not pd.isna(f):
                break
        else:
            _skip = True

        if _skip:
            continue

        values = {
            "effective_from": route["EFFECTIVE FROM"],
            "effective_to": route["EFFECTIVE TO"],
            "company": services.get(route["Service"]),
            "start_point": points.get(
                (
                    route["POL COUNTRY"],
                    route["POL FULL NAME"],
                )
            ),
            "end_point": points.get(
                (
                    route["POD COUNTRY"],
                    route["POD FULL NAME"],
                )
            ),
        }
        values.update({v: _parse_price(route[k]) for k, v in price_fields.items()})
        container = containers.get(
            (
                route["CONTAINER TYPE"],
                route["CONTAINER SIZE"],
            )
            if pd.isna(route["Container weight limit"])
            else (
                route["CONTAINER TYPE"],
                route["CONTAINER SIZE"],
                route["Container weight limit"],
            )
        )
        if isinstance(container, list):
            for cont in container:
                print(cont)
                models.append(model_type(**values, container=cont))
        else:
            models.append(model_type(**values, container=container))

    return models


def _parse_price(s):
    if pd.isna(s):
        return None
    if isinstance(s, (int, float)):
        return float(s)
    return float(s.replace(" ", "").replace("$", ""))


def uid_extract(orm_obj):
    return tuple(getattr(orm_obj, idx) for idx in orm_obj.uid)


async def get_all_from_db(obj, session):
    _type = type(obj)
    return {
        uid_extract(obj): obj
        for obj in (await session.execute(select(_type))).scalars().all()
    }


def compare(objects_local, objects_db):
    new_items = []
    for uid, obj in objects_local.items():
        if uid in objects_db:
            obj.id = objects_db[uid].id
        else:
            new_items.append(obj)
    return new_items


async def select_only_new(objs, session):
    objs = list(objs.values())
    return compare(
        {uid_extract(o): o for o in objs}, await get_all_from_db(objs[0], session)
    )


async def write_entities(entities, session):
    entities = await select_only_new(entities, session)
    if entities:
        session.add_all(entities)


async def write_independent_data(services, points, containers, session):
    await write_entities(services, session)
    await write_entities(containers, session)
    await write_entities(points, session)
    await session.flush()


async def write_routes(routes, session):
    for route in routes:
        route.company = await session.merge(route.company, load=True)
        route.container = await session.merge(route.container, load=True)
        route.start_point = await session.merge(route.start_point, load=True)
        route.end_point = await session.merge(route.end_point, load=True)
    session.add_all(routes)
    await session.flush()


async def main():
    df_rail = pd.read_csv(
        "rail-data-updated.csv",
        index_col=None,
        delimiter=";",
        parse_dates=["EFFECTIVE FROM", "EFFECTIVE TO"],
    )
    df_sea = pd.read_csv(
        "sea-data-updated.csv",
        index_col=None,
        delimiter=";",
        parse_dates=["EFFECTIVE FROM", "EFFECTIVE TO"],
    )
    df = pd.concat([df_sea, df_rail])
    services, points, containers = extract_data(df)
    services, points, containers, typed_containers = create_independent_models(
        services, points, containers
    )
    print(", ".join([s.name for s in services.values()]))
    print(", ".join([p.country + " " + p.city for p in points.values()]))
    print(", ".join([c.name for c in containers.values()]))
    rail_routes = create_routes(
        df_rail,
        RailRouteModel,
        {"Price, RUB": "price", "Drop, $": "drop", "Guard": "guard"},
        ["Price, RUB"],
        services,
        points,
        containers,
    )
    sea_routes = create_routes(
        df_sea,
        SeaRouteModel,
        {"FILO": "filo", "FIFO": "fifo"},
        ["FIFO", "FILO"],
        services,
        points,
        typed_containers,
    )
    async with database.session() as session:
        await write_independent_data(services, points, containers, session)
        await write_routes(rail_routes, session)
        await write_routes(sea_routes, session)
        await session.commit()


asyncio.run(main())
