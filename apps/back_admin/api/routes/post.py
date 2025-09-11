import pandas as pd
from fastapi import APIRouter, HTTPException

from back_admin.database import database
from back_admin.models import (
    RailRouteModel,
    SeaRouteModel,
)
from back_admin.models.requests.route import (
    EditRouteRequest,
    FilterRoutesRequest, AddRouteRequest, DeleteRoutesRequest,
)
from sqlalchemy import delete, func, select, update
from sqlalchemy.exc import InvalidRequestError
from sqlalchemy.orm import joinedload

router = APIRouter(prefix="/routes", tags=["routes-admin"])


async def exe_q(q, return_scalar=False):
    async with database.session() as session:
        temp = await session.execute(q)
        return temp.scalar() if return_scalar else temp.scalars().all()


def parse_date(date_value: str):
    if pd.isna(date_value):
        return None
    if isinstance(date_value, str):
        try:
            return pd.to_datetime(date_value, dayfirst=True).date()
        except:
            return None
    return pd.to_datetime(date_value).date()


def get_route_class(_type: str):
    return RailRouteModel if _type == "rail" else SeaRouteModel


def parseRoute(_route, _type):
    return {
        "route_type": _type,
        "id": _route.id,
        "company": _route.company,
        "container": _route.container,
        "start_point": _route.start_point,
        "end_point": _route.end_point,
        "effective_from": _route.effective_from,
        "effective_to": _route.effective_to,
        "price": [
            {
                "type": "filo",
                "value": getattr(_route, "filo", None),
                "currency": "USD",
            },
            {
                "type": "fifo",
                "value": getattr(_route, "fifo", None),
                "currency": "USD",
            },
            {
                "type": "drop",
                "value": getattr(_route, "drop", None),
                "currency": "USD",
            },
            {
                "type": "price",
                "value": getattr(_route, "price", None) if not hasattr(_route, "filo") else None,
                "currency": "RUB",
            },
            {
                "type": "guard",
                "value": getattr(_route, "guard", None),
                "currency": "USD",
            }, ],
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
    ).where(
        RailRouteModel.batch_id.is_(None) if not _filter.batch_id else RailRouteModel.batch_id == _filter.batch_id,
    )

    sea_stmt = select(
        SeaRouteModel,
    ).options(
        joinedload(SeaRouteModel.container),
        joinedload(SeaRouteModel.company),
        joinedload(SeaRouteModel.start_point),
        joinedload(SeaRouteModel.end_point),
    ).where(
        SeaRouteModel.batch_id.is_(None) if not _filter.batch_id else SeaRouteModel.batch_id == _filter.batch_id,
    )

    no_key_fields = ["effective_from", "effective_to", "route_type"]

    for column, value in _filter.filter_fields:
        if not value:
            continue

        if column not in no_key_fields:
            rail_stmt = rail_stmt.where(
                getattr(RailRouteModel, column) == value,
            )
            sea_stmt = sea_stmt.where(
                getattr(SeaRouteModel, column) == value,
            )

    # Dates filter
    if _filter.filter_fields.effective_from:
        date_from = parse_date(_filter.filter_fields.effective_from)

        rail_stmt = rail_stmt.where(
            RailRouteModel.effective_from >= date_from,
        )

        sea_stmt = sea_stmt.where(
            SeaRouteModel.effective_from >= date_from,
        )

    if _filter.filter_fields.effective_to:
        date_to = parse_date(_filter.filter_fields.effective_to)

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
async def addRoute(route_to_add: AddRouteRequest):
    date_from = parse_date(route_to_add.effective_from)
    date_to = parse_date(route_to_add.effective_to)

    if getattr(route_to_add.price, "drop", None):
        new_route = RailRouteModel(
            company_id=route_to_add.company_id,
            container_id=route_to_add.container_id,
            start_point_id=route_to_add.start_point_id,
            end_point_id=route_to_add.end_point_id,
            effective_from=date_from,
            effective_to=date_to,
            price=route_to_add.price.price,
            drop=route_to_add.price.drop,
            guard=route_to_add.price.guard,
        )
        route_type = "rail"

    else:
        new_route = SeaRouteModel(
            company_id=route_to_add.company_id,
            container_id=route_to_add.container_id,
            start_point_id=route_to_add.start_point_id,
            end_point_id=route_to_add.end_point_id,
            effective_from=date_from,
            effective_to=date_to,
            filo=route_to_add.price.filo,
            fifo=route_to_add.price.fifo,
        )
        route_type = "sea"

    async with database.session() as session:
        try:
            session.add(new_route)
            await session.flush()

            route_class = RailRouteModel if route_type == "rail" else SeaRouteModel
            get_route_stmt = select(
                route_class,
            ).options(
                joinedload(route_class.container),
                joinedload(route_class.company),
                joinedload(route_class.start_point),
                joinedload(route_class.end_point),
            ).where(
                route_class.id == new_route.id,
            )

            temp = await session.execute(get_route_stmt)
            joined_res = temp.scalar()

        except InvalidRequestError as e:
            raise HTTPException(
                status_code=400,
                detail=str(e)
            )

    result = parseRoute(joined_res, _type=route_type)

    return {
        "status": "OK",
        "new_route": result,
    }


@router.put("/edit")
async def editRoute(edit_route: EditRouteRequest):
    is_rail, is_sea = edit_route.edit_params.route_type == "rail", edit_route.edit_params.route_type == "sea"
    if is_rail:
        route_class = RailRouteModel
    elif is_sea:
        route_class = SeaRouteModel
    else:
        raise HTTPException(
            status_code=400,
            detail=f"Incorrect route type '{edit_route.edit_params.route_type}'"
        )

    edit_route_stmt = update(
        route_class,
    ).where(
        route_class.id == edit_route.route_id,
    ).options(
        joinedload(route_class.container),
        joinedload(route_class.company),
        joinedload(route_class.start_point),
        joinedload(route_class.end_point),
    )

    route_with_current_dates = await exe_q(select(
        route_class
    ).where(
        route_class.id == edit_route.route_id,
    ), True)

    # Start point
    if edit_route.edit_params.start_point_id:
        edit_route_stmt = edit_route_stmt.values(
            start_point_id=edit_route.edit_params.start_point_id,
        )

    # End point
    if edit_route.edit_params.end_point_id:
        edit_route_stmt = edit_route_stmt.values(
            end_point_id=edit_route.edit_params.end_point_id,
        )

    # Company
    if edit_route.edit_params.company_id:
        edit_route_stmt = edit_route_stmt.values(
            company_id=edit_route.edit_params.company_id,
        )

    # Container
    if edit_route.edit_params.container_id:
        edit_route_stmt = edit_route_stmt.values(
            container_id=edit_route.edit_params.container_id,
        )

    # Dates
    if edit_route.edit_params.effective_from:
        date_from = parse_date(edit_route.edit_params.effective_from)

        if date_from > route_with_current_dates.effective_to:
            raise HTTPException(
                status_code=400,
                detail=f"Incorrect dates {edit_route.edit_params.effective_from} - {edit_route.edit_params.effective_to}"
            )

        edit_route_stmt = edit_route_stmt.values(
            effective_from=edit_route.edit_params.effective_from,
        )

    if edit_route.edit_params.effective_to:
        date_to = parse_date(edit_route.edit_params.effective_to)

        if date_to < route_with_current_dates.effective_from or date_from >= date_to:
            raise HTTPException(
                status_code=400,
                detail=f"Incorrect dates {edit_route.edit_params.effective_from} - {edit_route.edit_params.effective_to}"
            )

        edit_route_stmt = edit_route_stmt.values(
            effective_to=edit_route.edit_params.effective_to,
        )

    # Prices
    if edit_route.edit_params.price:
        if is_rail:
            if edit_route.edit_params.price.price:
                edit_route_stmt = edit_route_stmt.values(
                    price=edit_route.edit_params.price.price,
                )
            if edit_route.edit_params.price.guard:
                edit_route_stmt = edit_route_stmt.values(
                    guard=edit_route.edit_params.price.guard,
                )
            if edit_route.edit_params.price.drop:
                edit_route_stmt = edit_route_stmt.values(
                    drop=edit_route.edit_params.price.drop,
                )

        if is_sea:
            if edit_route.edit_params.price.fifo:
                edit_route_stmt = edit_route_stmt.values(
                    fifo=edit_route.edit_params.price.fifo,
                )
            if edit_route.edit_params.price.filo:
                edit_route_stmt = edit_route_stmt.values(
                    filo=edit_route.edit_params.price.filo,
                )

    async with database.session() as session:
        route_to_change = await session.execute(edit_route_stmt)

    if not route_to_change:
        raise HTTPException(
            status_code=400,
            detail="Incorrect route id"
        )

    return {
        "status": "OK",
        "changed_route": route_to_change,
    }


@router.post("/delete")
async def deleteRoutes(ids_dict: DeleteRoutesRequest):
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
        "deleted_routes": removed_count,
    }
