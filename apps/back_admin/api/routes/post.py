from datetime import datetime

from fastapi import APIRouter, HTTPException

from back_admin.database import database
from back_admin.models import RailRouteModel, SeaRouteModel
from back_admin.models.requests.route import (
    AddRouteRequest,
    DeleteRoutesRequest,
    EditRouteRequest,
    FilterRoutesRequest,
)
from sqlalchemy import and_, delete, func, not_, or_, select, update
from sqlalchemy.exc import InvalidRequestError
from sqlalchemy.orm import joinedload

router = APIRouter(prefix="/routes", tags=["routes-admin"])


async def exe_q(q, return_scalar=False):
    async with database.session() as session:
        temp = await session.execute(q)
        return temp.scalar() if return_scalar else temp.scalars().all()


def parse_date(date_value: str):
    return datetime.strptime(date_value, "%d.%m.%Y").date()


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
                "value": getattr(_route, "price", None) if _type == "rail" else None,
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
    )

    sea_stmt = select(
        SeaRouteModel,
    ).options(
        joinedload(SeaRouteModel.container),
        joinedload(SeaRouteModel.company),
        joinedload(SeaRouteModel.start_point),
        joinedload(SeaRouteModel.end_point),
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
    if _filter.filter_fields.effective_from and _filter.filter_fields.effective_to:
        date_from = parse_date(_filter.filter_fields.effective_from)
        date_to = parse_date(_filter.filter_fields.effective_to)

        rail_stmt = rail_stmt.where(
            not_(or_(and_(RailRouteModel.effective_from < date_from,
                          RailRouteModel.effective_to < date_from),
                     and_(RailRouteModel.effective_from > date_to,
                          RailRouteModel.effective_to > date_to))),
        )

        sea_stmt = sea_stmt.where(
            not_(or_(and_(SeaRouteModel.effective_from < date_from,
                          SeaRouteModel.effective_to < date_from),
                     and_(SeaRouteModel.effective_from > date_to,
                          SeaRouteModel.effective_to > date_to))),
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

    if route_to_add.route_type == "rail":
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

    async with database.session() as session:
        try:
            session.add(new_route)
            await session.flush()  # todo: try except duplicateError

            route_class = RailRouteModel if route_to_add.route_type == "rail" else SeaRouteModel

            temp = await session.execute(
                select(
                    route_class,
                ).where(
                    route_class.id == new_route.id,
                ).options(
                    joinedload(route_class.container),
                    joinedload(route_class.company),
                    joinedload(route_class.start_point),
                    joinedload(route_class.end_point),
                )
            )
            joined_res = temp.scalar()

        except InvalidRequestError as e:
            raise HTTPException(
                status_code=400,
                detail=str(e)
            )

    result = parseRoute(joined_res, _type=route_to_add.route_type)

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

    # If not id like this
    correct_route_id = await exe_q(select(
        route_class.id,
    ).where(
        route_class.id == edit_route.route_id,
    ), True)

    if not correct_route_id:
        raise HTTPException(
            status_code=404,
            detail=f"Incorrect route id '{edit_route.route_id}'"
        )

    edit_route_stmt = update(
        route_class,
    ).where(
        route_class.id == edit_route.route_id,
    )

    route_with_current_dates = await exe_q(select(
        route_class
    ).where(
        route_class.id == edit_route.route_id,
    ), True)

    current_date_from = route_with_current_dates.effective_from.date()
    current_date_to = route_with_current_dates.effective_to.date()

    update_values = {}
    fields_to_check = ['effective_from', 'effective_to', 'container_id', 'company_id', 'start_point_id', 'end_point_id']
    rail_price = ['price', 'drop', 'guard']
    sea_price = ['filo', 'fifo']

    date_from = parse_date(edit_route.edit_params.effective_from) if edit_route.edit_params.effective_from else datetime.fromtimestamp(0).date()
    date_to = parse_date(edit_route.edit_params.effective_to) if edit_route.edit_params.effective_to else datetime.fromtimestamp(10000000000).date()

    for field in fields_to_check:
        value = getattr(edit_route.edit_params, field, None)
        if value:
            if field == 'effective_from':
                if (not edit_route.edit_params.effective_to and date_from > current_date_to) or (edit_route.edit_params.effective_to and date_from > date_to):
                    raise HTTPException(
                        status_code=400,
                        detail=f"Incorrect dates: effective_from={edit_route.edit_params.effective_from}|effective_to={edit_route.edit_params.effective_to};"
                               f"\nCurrent dates: current_effective_from={current_date_from}|current_effective_to={current_date_to}"
                    )
                update_values[field] = date_from
                continue

            if field == 'effective_to':
                if (not edit_route.edit_params.effective_from and date_to < current_date_from) or (edit_route.edit_params.effective_from and date_to < date_from):
                    raise HTTPException(
                        status_code=400,
                        detail=f"Incorrect dates: effective_from={edit_route.edit_params.effective_from}|effective_to={edit_route.edit_params.effective_to};"
                               f"\nCurrent dates: current_effective_from={current_date_from}|current_effective_to={current_date_to}"
                    )
                update_values[field] = date_to
                continue

            update_values[field] = value

    if is_rail:
        for field in rail_price:
            value = getattr(edit_route.edit_params.price, field, None)
            if value:
                update_values[field] = value
    else:
        for field in sea_price:
            value = getattr(edit_route.edit_params.price, field, None)
            if value:
                update_values[field] = value

    edit_route_stmt = edit_route_stmt.values(**update_values)

    async with database.session() as session:
        await session.execute(edit_route_stmt)
        await session.commit()

        route_to_change = await exe_q(
            select(
                route_class,
            ).where(
                route_class.id == edit_route.route_id,
            ).options(
                joinedload(route_class.container),
                joinedload(route_class.company),
                joinedload(route_class.start_point),
                joinedload(route_class.end_point),
            ), True)

    result = parseRoute(route_to_change, _type="rail" if is_rail else "sea")

    return {
        "status": "OK",
        "changed_route": result,
    }


@router.delete("/delete")
async def deleteRoutes(ids_dict: DeleteRoutesRequest):
    async with database.session() as session:
        count_sea, count_rail = 0, 0

        if ids_dict.sea:
            sea_count_stmt = select(
                func.count(SeaRouteModel.id),
            ).where(
                SeaRouteModel.id.in_(ids_dict.sea),
            )
            count_sea = await exe_q(sea_count_stmt, True)

            sea_delete_stmt = delete(SeaRouteModel).where(
                SeaRouteModel.id.in_(ids_dict.sea)
            )
            await session.execute(sea_delete_stmt)

        if ids_dict.rail:
            rail_count_stmt = select(
                func.count(RailRouteModel.id),
            ).where(
                RailRouteModel.id.in_(ids_dict.rail),
            )
            count_rail = await exe_q(rail_count_stmt, True)

            rail_delete_stmt = delete(RailRouteModel).where(
                RailRouteModel.id.in_(ids_dict.rail)
            )
            await session.execute(rail_delete_stmt)

    removed_count = count_sea + count_rail

    return {
        "status": "OK",
        "deleted_routes": removed_count,
    }
