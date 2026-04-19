from collections.abc import Iterable

import pandas as pd
from backend_admin.models.upoader_fields_config import UploaderFieldsConfig
from module_data_internal.schemas import (
    CompanyModel,
    ContainerModel,
    ContainerOwner,
    ContainerShipmentTerms,
    ContainerTransferTerms,
    ContainerType,
    DropModel,
    PointModel,
    PriceModel,
    RouteModel,
    RouteType,
)
from sqlalchemy import select
from sqlalchemy.orm import joinedload

from .errors import (
    InvalidDroppRow,
    InvalidRouteTypeException,
    NoPriceInRouteException,
    PointNotFoundException,
)
from .helpers import nan_to_none_mapper

ContainerRawType = dict[str, str | int | ContainerType]
ContainerUid = tuple[int, int, int]
ContainerStore = dict[ContainerUid, ContainerModel]

CompaniesStore = dict[str, CompanyModel]

PointsStore = list[PointModel]
PointsHashedStore = dict[str, PointModel]


async def load_companies(db_session, companies) -> CompaniesStore:
    models = {}
    existing_models = (await db_session.execute(select(CompanyModel))).scalars().all()

    for company in existing_models:
        models[company.name] = company

    for company in companies:
        if not models.get(company):
            models[company] = await db_session.merge(
                CompanyModel(name=company),
                load=True,
            )

    await db_session.commit()
    return models


async def load_points(db_session, df) -> PointsStore:
    models: list[PointModel | None] = [None] * len(df)
    existing_points = (await db_session.execute(select(PointModel))).scalars().all()
    existing_models_lower = {point.city.lower(): point for point in existing_points}

    for i, row in enumerate(df.itertuples()):
        arguments = row._asdict()
        del arguments["Index"]

        point = existing_models_lower.get(arguments["city"].lower())
        if not point:
            point = await db_session.merge(
                PointModel(**arguments),
                load=True,
            )
            existing_models_lower[point.city.lower()] = point

        models[i] = point

    await db_session.commit()
    return models  # type: ignore[return-value]


async def load_containers(db_session, containers: list[ContainerRawType]) -> ContainerStore:
    models = {}
    existing_models = (await db_session.execute(select(ContainerModel))).scalars().all()

    for container in existing_models:
        models[(
            container.size,
            container.weight_from,
            container.weight_to,
        )] = container

    for container in containers:
        container_complex_id = (
            container["size"],
            container["weight_from"],
            container["weight_to"],
        )
        if not models.get(container_complex_id):
            container["type"] = ContainerType(container["type"])
            models[container_complex_id] = await db_session.merge(
                ContainerModel(**container),
                load=True,
            )

    await db_session.commit()
    return models


def create_route(  # noqa: C901
    containers: ContainerStore,
    companies: CompaniesStore,
    points: PointsHashedStore,
    row,
    fc: UploaderFieldsConfig,
    route_type: RouteType,
):
    # Container terms
    ctt = ContainerTransferTerms(row[fc.container_transfer_terms].upper())
    cst = ContainerShipmentTerms(row[fc.container_shipment_terms].upper())
    co = ContainerOwner(row[fc.container_condition].upper())

    sea_prices = None, None
    rail_prices = None, None, None

    if route_type is RouteType.SEA:
        sea_prices = tuple(map(nan_to_none_mapper, (
            row[fc.sea_20dc],
            row[fc.sea_40hc],
        )))

        if not any(sea_prices):
            raise NoPriceInRouteException

    elif route_type is RouteType.RAIL:
        rail_prices = tuple(map(nan_to_none_mapper, (
            row[fc.rail_20dc24t],
            row[fc.rail_20dc28t],
            row[fc.rail_40hc],
        )))

        if not any(rail_prices):
            raise NoPriceInRouteException

    else:
        raise InvalidRouteTypeException(route_type)

    company = companies[row[fc.company].upper()]

    try:
        start_point = points[row[fc.start_point].lower()]
        end_point = points[row[fc.end_point].lower()]
    except KeyError as e:
        raise PointNotFoundException(e.args[0]) from e

    effective_from = row[fc.effective_from]
    effective_to = row[fc.effective_to]

    route = RouteModel(
        type=RouteType(route_type),
        company=company,
        start_point=start_point,
        end_point=end_point,
        effective_from=effective_from,
        effective_to=effective_to,
        comment=nan_to_none_mapper(row[fc.comment]),
        container_transfer_terms=ctt,
        container_shipment_terms=cst,
        container_owner=co,
    )

    conversation = nan_to_none_mapper(row[fc.conversation_percents])

    if route.type is RouteType.SEA:
        dc20_24t = sea_prices[0]
        dc20_24t_currency = "USD" if pd.isna(row[fc.sea_20dc_currency]) else row[fc.sea_20dc_currency].strip().upper()
        dc20_28t = dc20_24t
        dc20_28t_currency = dc20_24t_currency
        hc40 = sea_prices[1]
        hc40_currency = "USD" if pd.isna(row[fc.sea_40hc_currency]) else row[fc.sea_40hc_currency].strip().upper()
    elif route.type is RouteType.RAIL:
        dc20_24t = rail_prices[0]
        dc20_24t_currency = (
            "РУБ" if pd.isna(row[fc.rail_20dc24t_currency]) else row[fc.rail_20dc24t_currency].strip().upper()
        )
        dc20_28t = rail_prices[1]
        dc20_28t_currency = (
            "РУБ" if pd.isna(row[fc.rail_20dc28t_currency]) else row[fc.rail_20dc28t_currency].strip().upper()
        )
        hc40 = rail_prices[2]
        hc40_currency = "РУБ" if pd.isna(row[fc.rail_40hc_currency]) else row[fc.rail_40hc_currency].strip().upper()
    else:
        raise InvalidRouteTypeException(route_type)

    if dc20_24t is not None:
        PriceModel(
            container=containers[(20, 0, 24)],
            route=route,
            currency=dc20_24t_currency,
            value=dc20_24t,
            conversation_percents=conversation,
        )
    if dc20_28t is not None:
        PriceModel(
            container=containers[(20, 24, 28)],
            route=route,
            currency=dc20_28t_currency,
            value=dc20_28t,
            conversation_percents=conversation,
        )
    if hc40 is not None:
        PriceModel(
            container=containers[(40, 0, 28)],
            route=route,
            currency=hc40_currency,
            value=hc40,
            conversation_percents=conversation,
        )

    return route


def create_dropp(
    containers: ContainerStore,
    companies: CompaniesStore,
    points: PointsHashedStore,
    row,
    fc: UploaderFieldsConfig,
):
    company = companies.get(row[fc.company].upper())
    start_point = points.get(row[fc.start_point].lower())
    end_point = points.get(row[fc.end_point].lower())
    effective_from = row[fc.effective_from]
    effective_to = row[fc.effective_to]

    currency = "USD"
    price_20dc = row[fc.drop20]
    price_40hc = row[fc.drop40]
    conversation_percents = row[fc.conversation_percents]

    if not all((company, start_point, end_point, effective_from, effective_to)):
        raise InvalidDroppRow

    base_config = {
        "start_point": start_point,
        "end_point": end_point,
        "company": company,
        "effective_from": effective_from,
        "effective_to": effective_to,
        "conversation_percents": conversation_percents,
        "currency": currency,
    }

    all_dropp: list[DropModel] = []
    if price_20dc and not pd.isna(price_20dc):
        all_dropp.extend((
            DropModel(**base_config, price=price_20dc, container=containers[(20, 0, 24)]),
            DropModel(**base_config, price=price_20dc, container=containers[(20, 24, 28)]),
        ))
    if price_40hc and not pd.isna(price_40hc):
        all_dropp.append(DropModel(**base_config, price=price_40hc, container=containers[(40, 0, 28)]))

    return all_dropp


async def load_routes(db_session, routes):
    existing_routes = (await db_session.execute(select(RouteModel).options(
        joinedload(RouteModel.start_point),
        joinedload(RouteModel.end_point),
        joinedload(RouteModel.company),
    ))).scalars().all()

    existing_routes_set = {(  # noqa: ECE001
        route.company.name,
        route.start_point.city,
        route.end_point.city,
        route.effective_from if isinstance(route.effective_from, str) else route.effective_from.date().isoformat(),
        route.effective_to if isinstance(route.effective_to, str) else route.effective_to.date().isoformat(),
    ) for route in existing_routes}

    for route in routes:
        route_key = (
            route.company.name,
            route.start_point.city,
            route.end_point.city,
            route.effective_from if isinstance(route.effective_from, str) else route.effective_from.date().isoformat(),
            route.effective_to if isinstance(route.effective_to, str) else route.effective_to.date().isoformat(),
        )
        if route_key in existing_routes_set:
            continue

        await db_session.merge(route)
        existing_routes_set.add(route_key)

    await db_session.commit()


async def load_dropp(db_session, dropp: list[Iterable[DropModel]]):
    existing_dropp = (await db_session.execute(select(DropModel).options(
        joinedload(DropModel.start_point),
        joinedload(DropModel.end_point),
        joinedload(DropModel.company),
        joinedload(DropModel.container),
    ))).scalars().all()

    existing_dropp_set = {(  # noqa: ECE001
        item.start_point.city,
        item.end_point.city,
        item.company.name,
        (item.container.size, item.container.weight_from, item.container.weight_to),
        item.effective_from if isinstance(item.effective_from, str) else item.effective_from.date().isoformat(),
        item.effective_to if isinstance(item.effective_to, str) else item.effective_to.date().isoformat(),
    ) for item in existing_dropp}

    for items_group in dropp:
        for item in items_group:
            dropp_key = (
                item.start_point.city,
                item.end_point.city,
                item.company.name,
                (item.container.size, item.container.weight_from, item.container.weight_to),
                item.effective_from if isinstance(item.effective_from, str) else item.effective_from.date().isoformat(),
                item.effective_to if isinstance(item.effective_to, str) else item.effective_to.date().isoformat(),
            )
            if dropp_key in existing_dropp_set:
                continue

            await db_session.merge(item)
            existing_dropp_set.add(dropp_key)

    await db_session.commit()
