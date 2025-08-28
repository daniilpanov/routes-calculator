import io
from datetime import datetime
from functools import partial

from fastapi import APIRouter, HTTPException, UploadFile

import pandas as pd
from back_admin.database import database
from back_admin.models import (
    CompanyModel,
    ContainerModel,
    PointModel,
    RailRouteModel,
    SeaRouteModel,
)
from back_admin.models.requests.route import (
    AddRouteRequest,
    DeleteManyRoutesRequest,
    EditRouteRequest,
    FilterRoutesRequest,
)
from sqlalchemy import delete, func, select, update
from sqlalchemy.exc import IntegrityError, InvalidRequestError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

router = APIRouter(prefix="/routes", tags=["routes"])


async def exe_q(q, return_scalar=False):
    async with database.session() as session:
        temp = await session.execute(q)
        return temp.scalar() if return_scalar else temp.scalars().all()


def parseDate(date):
    return datetime.strptime(date, "%d.%m.%Y").date()


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
            }, ],
    }
    return res


async def getPointIdAndColumn(which_point, name):
    country, city = name.split(", ")
    stmt = select(
        PointModel.id,
    ).where(
        PointModel.RU_country == country,
        PointModel.RU_city == city,
    )
    data = await exe_q(stmt, True)
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


keys_map = {
    "start_point": partial(getPointIdAndColumn, "start_point_id"),
    "end_point": partial(getPointIdAndColumn, "end_point_id"),
    "company": getCompanyIdAndColumn,
    "container": getContainerIdAndColumn,
    "effective_from": None,
    "effective_to": None,
    "route_type": None,
}


@router.post("")
async def getRoutes(_filter: FilterRoutesRequest):
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

    for column, value in _filter.filter_fields:
        if not value or not keys_map[column]:  # todo make correct route_type check
            continue

        if keys_map[column]:
            value, column = await keys_map[column](value)

        rail_stmt = rail_stmt.where(
            getattr(RailRouteModel, column) == value,
        )

        sea_stmt = sea_stmt.where(
            getattr(SeaRouteModel, column) == value,
        )

    # Dates filter
    if _filter.filter_fields.effective_from:
        date_from = parseDate(_filter.filter_fields.effective_from)

        rail_stmt = rail_stmt.where(
            RailRouteModel.effective_from >= date_from,
        )

        sea_stmt = sea_stmt.where(
            SeaRouteModel.effective_from >= date_from,
        )

    if _filter.filter_fields.effective_to:
        date_to = parseDate(_filter.filter_fields.effective_to)

        rail_stmt = rail_stmt.where(
            RailRouteModel.effective_to <= date_to,
        )

        sea_stmt = sea_stmt.where(
            SeaRouteModel.effective_to <= date_to,
        )

    rail_rows = await exe_q(
        rail_stmt)  # todo: Add price filters for every compare oper ['=', '!=', '<', '>', '<=', '>=']
    sea_rows = await exe_q(sea_stmt)

    # Route type filter
    if _filter.filter_fields.route_type == "rail":
        all_rows = rail_rows
    elif _filter.filter_fields.route_type == "sea":
        all_rows = sea_rows
    else:
        all_rows = rail_rows + sea_rows

    all_routes = [
        parseRoute(route, _type="rail" if isinstance(route, RailRouteModel) else "sea")
        for route in all_rows
    ]

    paginated_rows = all_routes[offset: offset + _filter.limit]
    total_count = len(all_rows)

    return {
        "status": "OK",
        "count": total_count,
        "routes": paginated_rows,
    }


@router.post("/add")
async def addRoute(route: AddRouteRequest):
    date_from = parseDate(route.effective_from)
    date_to = parseDate(route.effective_to)

    if date_from >= date_to:
        raise HTTPException(
            status_code=400,
            detail=f"Dates '{route.effective_from} - {route.effective_to}' invalid"
        )

    # Start point parse
    start_country, start_city = route.start_point_name.split(", ")

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
    end_country, end_city = route.end_point_name.split(", ")

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
        try:
            session.add(new_route)
        except InvalidRequestError as e:
            raise HTTPException(
                status_code=400,
                detail=f"Points must be different;{e}"
            )

    result = parseRoute(new_route, _type=route_type)

    return {
        "status": "OK",
        "new_route": result,
    }


@router.put("/edit")
async def editRoute(edit_route: EditRouteRequest):
    is_rail, is_sea = edit_route.other_params.route_type == "rail", edit_route.other_params.route_type == "sea"
    if is_rail:
        route_class = RailRouteModel
    elif is_sea:
        route_class = SeaRouteModel
    else:
        raise HTTPException(
            status_code=400,
            detail=f"Incorrect route type '{edit_route.other_params.route_type}'"
        )

    get_route_stmt = update(
        route_class,
    ).where(
        route_class.id == edit_route.route_id,
    ).options(
        joinedload(route_class.container),
        joinedload(route_class.company),
        joinedload(route_class.start_point),
        joinedload(route_class.end_point),
    )

    # Start point
    if edit_route.other_params.start_point:
        temp = await getPointIdAndColumn("", edit_route.other_params.start_point)

        new_start_point_id = temp[0]
        get_route_stmt = get_route_stmt.values(
            start_point_id=new_start_point_id,
        )

    # End point
    if edit_route.other_params.end_point:
        temp = await getPointIdAndColumn("", edit_route.other_params.end_point)
        if not temp:
            raise HTTPException(
                status_code=400,
                detail=f"Incorrect end point '{edit_route.other_params.end_point}'"
            )

        new_end_point_id = temp[0]

        get_route_stmt = get_route_stmt.values(
            end_point_id=new_end_point_id,
        )

    # Company
    if edit_route.other_params.company:
        temp = await getCompanyIdAndColumn(edit_route.other_params.company)

        new_company_id = temp[0]
        get_route_stmt = get_route_stmt.values(
            company_id=new_company_id,
        )

    # Container
    if edit_route.other_params.container:
        temp = await getContainerIdAndColumn(edit_route.other_params.container)

        new_container_id = temp[0]
        get_route_stmt = get_route_stmt.values(
            container_id=new_container_id,
        )

    # Dates
    if edit_route.other_params.effective_from:
        date_from = parseDate(edit_route.other_params.effective_from)
        date_to = parseDate(edit_route.other_params.effective_to)

        if date_from > date_to:  # todo make some changes ...
            raise HTTPException(
                status_code=400,
                detail=f"Incorrect dates {edit_route.other_params.effective_from} - {edit_route.other_params.effective_to}"
            )

        get_route_stmt = get_route_stmt.values(
            effective_from=edit_route.other_params.effective_from,
        )

    if edit_route.other_params.effective_to:
        get_route_stmt = get_route_stmt.values(
            effective_to=edit_route.other_params.effective_to,
        )

    # Prices
    if edit_route.other_params.price:
        if is_rail:
            if edit_route.other_params.price.price:
                get_route_stmt = get_route_stmt.values(
                    price=edit_route.other_params.price.price,
                )
            if edit_route.other_params.price.guard:
                get_route_stmt = get_route_stmt.values(
                    guard=edit_route.other_params.price.guard,
                )
            if edit_route.other_params.price.drop:
                get_route_stmt = get_route_stmt.values(
                    drop=edit_route.other_params.price.drop,
                )

        if is_sea:
            if edit_route.other_params.price.fifo:
                get_route_stmt = get_route_stmt.values(
                    fifo=edit_route.other_params.price.fifo,
                )
            if edit_route.other_params.price.filo:
                get_route_stmt = get_route_stmt.values(
                    filo=edit_route.other_params.price.filo,
                )

    async with database.session() as session:
        route_to_change = await session.execute(get_route_stmt)

    if not route_to_change:
        raise HTTPException(
            status_code=400,
            detail="Incorrect route id"
        )

    return {
        "status": "OK",
        "changed_route": route_to_change,
    }


@router.delete("/delete")
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

    return {
        "status": "OK",
        "route_id": route_id,
    }


@router.post("/delete-many")
async def deleteMany(ids_dict: DeleteManyRoutesRequest):
    async with database.session() as session:
        rail_count_stmt = select(
            func.count(RailRouteModel.id),
        ).where(
            RailRouteModel.id.in_(ids_dict.rail),
        )

        sea_count_stmt = select(
            func.count(SeaRouteModel.id),
        ).where(
            SeaRouteModel.id.in_(ids_dict.sea),
        )

        count_sea = await exe_q(sea_count_stmt, True)
        count_rail = await exe_q(rail_count_stmt, True)
        removed_count = count_sea + count_rail

        if ids_dict.sea:
            sea_delete_stmt = delete(SeaRouteModel).where(
                SeaRouteModel.id.in_(ids_dict.sea)
            )
            await session.execute(sea_delete_stmt)

        if ids_dict.rail:
            rail_delete_stmt = delete(RailRouteModel).where(
                RailRouteModel.id.in_(ids_dict.rail)
            )
            await session.execute(rail_delete_stmt)

    return {
        "status": "OK",
        "deleted_routes": f"Removed {removed_count} routes",
    }


@router.post("/data-import")
async def dataImport(file: UploadFile):
    file_extension = file.filename.rsplit('.', maxsplit=1)[-1]

    if file_extension == "csv":
        contents = await file.read()
        df = pd.read_csv(io.BytesIO(contents))

    elif file_extension == "xlsx":
        contents = await file.read()
        df = pd.read_excel(io.BytesIO(contents))

    else:
        raise HTTPException(
            status_code=400,
            detail="Wrong file extension. Allowed only CSV, XLSX"
        )

    if 'fifo' in df.columns or 'filo' in df.columns:
        route_model = SeaRouteModel
        table_name = "sea_routes"
    elif 'price' in df.columns and 'drop' in df.columns:
        route_model = RailRouteModel
        table_name = "rail_routes"
    else:
        raise HTTPException(
            status_code=400,
            detail="Unknown file format. Cannot determine route type"
        )

    total_count = 0

    try:
        for _, row in df.iterrows():
            effective_from = pd.to_datetime(row['effective_from']).date() if 'effective_from' in row else None
            effective_to = pd.to_datetime(row['effective_to']).date() if 'effective_to' in row else None

            route_data = {
                'company_id': int(row['company_id']),
                'container_id': int(row['container_id']),
                'start_point_id': int(row['start_point_id']),
                'end_point_id': int(row['end_point_id']),
                'effective_from': effective_from,
                'effective_to': effective_to,
            }

            if route_model == SeaRouteModel:
                route_data['fifo'] = float(row['fifo']) if 'fifo' in row and pd.notna(row['fifo']) else None
                route_data['filo'] = float(row['filo']) if 'filo' in row and pd.notna(row['filo']) else None
            else:
                route_data['price'] = float(row['price'])
                route_data['drop'] = float(row['drop'])
                route_data['guard'] = float(row['guard']) if 'guard' in row and pd.notna(row['guard']) else None

            async with database.session() as session:
                session: AsyncSession
                existing = session.execute(select(
                    route_model
                ).where(**{
                    k: v for k, v in route_data.items()
                    if k in route_model.uid
                })
                                           )

                if existing:
                    for key, value in route_data.items():
                        setattr(existing, key, value)
                else:
                    new_route = route_model(**route_data)
                    session.add(new_route)

            total_count += 1

    except IntegrityError as e:
        raise HTTPException(
            status_code=400,
            detail=f"Database integrity error: {str(e)}"
        )
    except ValueError as e:
        raise HTTPException(
            status_code=400,
            detail=f"Data conversion error: {str(e)}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Unexpected error: {str(e)}"
        )

    return {
        "status": "OK",
        "count": total_count,
        "file": file.filename,
    }
