import datetime

import pandas as pd
from dotenv import load_dotenv
from fastapi import APIRouter
from sqlalchemy import select

from back_admin.models.route import BatchModel

load_dotenv(".env.local") or load_dotenv("../.env.local")

from back_admin.models import (
    CompanyModel,
    ContainerModel,
    PointModel,
)

router = APIRouter(prefix="/r", tags=["r"])


def extract_data(df: pd.DataFrame, company_col):
    services = df[company_col].unique()

    points = pd.concat(  # noqa: ECE001
        [
            df[[company_col, "POL COUNTRY", "POL FULL NAME"]].rename(
                columns={"POL COUNTRY": "Country", "POL FULL NAME": "City"},
            ),
            df[[company_col, "POD COUNTRY", "POD FULL NAME"]].rename(
                columns={"POD COUNTRY": "Country", "POD FULL NAME": "City"},
            ),
        ]
    ).drop_duplicates()

    containers = df[
        ["CONTAINER TYPE", "CONTAINER SIZE", "Container weight limit"]
    ].drop_duplicates()

    return services, points, containers


def group_containers(containers):
    container_models = {}
    container_typed_models = {}

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
            name=f"{_size}'{_type} ≤ {int(_weight_to)}t",
        )
        container_models[(_type, _size, _weight_to)] = inst
        container_typed_models.setdefault((_type, _size), []).append(inst)

    return container_models, container_typed_models


def group_containers_from_db(containers):
    container_models = {}
    container_typed_models = {}

    for inst in containers:
        container_models[(inst.type.value, str(int(inst.size)), str(int(inst.weight_to)))] = inst
        container_typed_models.setdefault((inst.type.value, str(inst.size)), []).append(inst)
    return container_models, container_typed_models


def create_independent_models(services, points, containers):
    service_models = {}
    point_models = {}

    for service in services:
        service_models[service] = CompanyModel(name=service)

    for _, point in points.iterrows():
        point_models[(point["Country"], point["City"])] = PointModel(  # todo: check parse for spaces
            country=point["Country"].strip(), city=point["City"].strip()
        )

    container_models, container_typed_models = group_containers(containers)

    return service_models, point_models, container_models, container_typed_models


def create_routes(
    df,
    model_type,
    price_fields,
    filter_fields,
    services,
    points,
    containers_3_keys,
    containers_2_keys,
    company_col,
    dates_col,
):
    models = []
    for _, route in df.iterrows():
        for ff in filter_fields:
            f = route.get(ff)
            if f and not pd.isna(f):
                break
        else:
            continue

        date_from, date_to = dates_col.split(";")
        values = {
            "effective_from": route[date_from],
            "effective_to": route[date_to],
            "company": services.get(route[company_col]),
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

        if pd.isna(route["Container weight limit"]):
            container_key = (
                route["CONTAINER TYPE"],
                route["CONTAINER SIZE"],
            )
            container = containers_2_keys.get(container_key)
        else:
            container_key = (
                route["CONTAINER TYPE"],
                route["CONTAINER SIZE"],
                route["Container weight limit"],
            )
            container = containers_3_keys.get(container_key)

        if isinstance(container, list):
            for cont in container:
                models.append(model_type(**values, container=cont))
        else:
            models.append(model_type(**values, container=container))

    return models


def _parse_price(s):
    if pd.isna(s):
        return None
    if isinstance(s, (int, float)):
        return float(s)
    return float(s.replace(" ", "").replace(",", ".").replace("$", ""))


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
    return len(entities)


async def write_independent_data(services, points, containers, session):
    if services:
        await write_entities(services, session)
    await write_entities(containers, session)
    print(points)
    count_points = await write_entities(points, session)
    await session.flush()
    return count_points


async def _merge_to_db(obj, model, session, lookup_field: str = "name"):

    lookup_value = getattr(obj, lookup_field)

    existing_obj = await session.execute(
        select(model).where(getattr(model, lookup_field) == lookup_value)
    )
    existing_obj = existing_obj.scalar_one_or_none()

    if existing_obj:
        print(existing_obj)
        return existing_obj
    else:
        print(obj)
        session.add(obj)
        return obj


async def write_routes(routes, session):
    new_batch_id = BatchModel(create_date=datetime.datetime.now())
    session.add(new_batch_id)
    await session.flush()

    for route in routes:
        route.company = await session.merge(route.company, load=True)
        route.container = await session.merge(route.container, load=True)
        route.start_point = await session.merge(route.start_point, load=True)
        route.end_point = await session.merge(route.end_point, load=True)
        route.batch_id = new_batch_id.id

    for route in routes:
        try:
            await session.merge(route)
            await session.commit()
        except Exception as e:
            await session.rollback()
            print(f"Merge error: {e}")
            continue
    await session.flush()

    return new_batch_id


def validate_route_data(df, company_col, dates_col):
    # Check duplicates.
    dup_check_cols = [
        "POL COUNTRY",
        "POL FULL NAME",
        "POD COUNTRY",
        "POD FULL NAME",
        "CONTAINER TYPE",
        "CONTAINER SIZE",
        "Container weight limit",
    ]

    if company_col:
        dup_check_cols += [company_col]
    if dates_col:
        dup_check_cols += dates_col.split(";")

    duplicates = df[df.duplicated(subset=dup_check_cols, keep=False)]
    if not duplicates.empty:
        print("Duplicates occurred:")
        print(duplicates.sort_values(dup_check_cols).to_string())
        raise ValueError("Duplicates occurred")


def parse_date(date_input):
    if pd.isna(date_input):
        return None

    if isinstance(date_input, pd.Timestamp):
        return date_input.to_pydatetime()

    if isinstance(date_input, datetime.datetime):
        return date_input

    if isinstance(date_input, str):
        try:
            formats = [
                "%d-%b-%y",
                "%d.%m.%Y",
                "%Y-%m-%d",
                "%d/%m/%Y",
                "%m/%d/%Y",
            ]

            for fmt in formats:
                try:
                    return pd.to_datetime(date_input, format=fmt, errors="raise")
                except ValueError:
                    continue

            return pd.to_datetime(date_input, errors='coerce')

        except Exception as e:
            print(f"Date parsing error: {date_input}, error: {e}")
            return None

    if isinstance(date_input, (int, float)):
        try:
            if 1000000000 < date_input < 2000000000:
                return datetime.datetime.fromtimestamp(int(date_input))
        except Exception as e:
            print(f"Number date parsing error: {date_input}, error: {e}")

    try:
        return pd.to_datetime(date_input, errors='coerce').to_pydatetime()

    except Exception as e:
        print(f"Could not parse date: {date_input}, error: {e}")
        return None
