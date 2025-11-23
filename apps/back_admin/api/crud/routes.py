from datetime import date, datetime
from typing import Any, Literal

from fastapi import Body, HTTPException, Path, Query

from back_admin.api.abstract_crud import AbstractCRUD
from back_admin.database import database
from back_admin.models import RailRouteModel, SeaRouteModel
from back_admin.models.requests.route import AddRouteRequest, DeleteRoutesRequest, EditRouteRequest
from pydantic import BaseModel, ConfigDict
from sqlalchemy import delete, func, select, update
from sqlalchemy.exc import InvalidRequestError
from sqlalchemy.orm import joinedload


class RoutePriceItem(BaseModel):
    type: str  # noqa: A003
    value: float | None
    currency: str


class RouteResponseSchema(BaseModel):
    route_type: str
    id: int  # noqa: A003
    company: Any
    container: Any
    start_point: Any
    end_point: Any
    effective_from: date
    effective_to: date
    price: list[RoutePriceItem]

    model_config = ConfigDict(from_attributes=True)


class RouteListResponse(BaseModel):
    status: str
    count: int
    routes: list[RouteResponseSchema]


class RouteCRUD(AbstractCRUD):
    def __init__(self):
        super().__init__()
        self._router.tags = ["routes-admin"]

    @property
    def prefix(self) -> str:
        return "routes"

    @property
    def orm_model_class(self):
        return RailRouteModel

    @property
    def instance_schema_class(self):
        return RouteResponseSchema

    def _initialize_routes(self):
        self._router.prefix = "/routes"

        self._router.add_api_route("/", self.get_routes, methods=["GET"])

        self._router.add_api_route("/{route_id}", self.add_route, methods=["POST"])
        self._router.add_api_route("/{route_id}", self.edit_route, methods=["PUT"])
        self._router.add_api_route("/{route_id}", self.delete_routes, methods=["DELETE"])

    @staticmethod
    async def _exe_q(q, return_scalar=False):
        async with database.session() as session:
            temp = await session.execute(q)
            return temp.scalar() if return_scalar else temp.scalars().all()

    @staticmethod
    def _parse_date(date_value: str | date | None) -> date | None:
        if not date_value:
            return None
        if isinstance(date_value, date):
            return date_value

        formats = ["%Y-%m-%d", "%d.%m.%Y"]
        for fmt in formats:
            try:
                return datetime.strptime(date_value, fmt).date()
            except ValueError:
                continue

        raise ValueError(f"Invalid date format: {date_value}. Expected YYYY-MM-DD or DD.MM.YYYY")

    def _parse_route_to_schema(self, _route, _type: str) -> dict:
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
                },
            ],
        }

    async def _get_filtered_routes_helper(
        self,
        page: int,
        limit: int,
        route_type: str | None = None,
        company_id: int | None = None,
        start_point_id: int | None = None,
        end_point_id: int | None = None,
        container_id: int | None = None,
        date_from: date | None = None,
        date_to: date | None = None
    ) -> dict:
        offset = (page - 1) * limit

        rail_stmt = select(RailRouteModel).options(
            joinedload(RailRouteModel.container),
            joinedload(RailRouteModel.company),
            joinedload(RailRouteModel.start_point),
            joinedload(RailRouteModel.end_point),
        )
        sea_stmt = select(SeaRouteModel).options(
            joinedload(SeaRouteModel.container),
            joinedload(SeaRouteModel.company),
            joinedload(SeaRouteModel.start_point),
            joinedload(SeaRouteModel.end_point),
        )

        if company_id:
            rail_stmt = rail_stmt.where(RailRouteModel.company_id == company_id)
            sea_stmt = sea_stmt.where(SeaRouteModel.company_id == company_id)

        if start_point_id:
            rail_stmt = rail_stmt.where(RailRouteModel.start_point_id == start_point_id)
            sea_stmt = sea_stmt.where(SeaRouteModel.start_point_id == start_point_id)

        if end_point_id:
            rail_stmt = rail_stmt.where(RailRouteModel.end_point_id == end_point_id)
            sea_stmt = sea_stmt.where(SeaRouteModel.end_point_id == end_point_id)

        if container_id:
            rail_stmt = rail_stmt.where(RailRouteModel.container_id == container_id)
            sea_stmt = sea_stmt.where(SeaRouteModel.container_id == container_id)

        if date_from:
            rail_stmt = rail_stmt.where(RailRouteModel.effective_to >= date_from)
            sea_stmt = sea_stmt.where(SeaRouteModel.effective_to >= date_from)

        if date_to:
            rail_stmt = rail_stmt.where(RailRouteModel.effective_from <= date_to)
            sea_stmt = sea_stmt.where(SeaRouteModel.effective_from <= date_to)

        rail_rows = []
        sea_rows = []

        if route_type == "rail" or route_type is None:
            rail_rows = await self._exe_q(rail_stmt)

        if route_type == "sea" or route_type is None:
            sea_rows = await self._exe_q(sea_stmt)

        all_routes = []
        all_routes.extend([self._parse_route_to_schema(r, "rail") for r in rail_rows])
        all_routes.extend([self._parse_route_to_schema(r, "sea") for r in sea_rows])

        all_routes.sort(key=lambda x: x['id'], reverse=True)

        total_count = len(all_routes)
        paginated_rows = all_routes[offset: offset + limit]

        return {
            "status": "OK",
            "count": total_count,
            "routes": paginated_rows,
        }

    async def get_routes(
        self,
        page: int = Query(1, ge=1, description="Номер страницы"),
        limit: int = Query(25, ge=1, description="Количество элементов"),
        route_type: Literal["rail", "sea"] | None = Query(None, description="Тип маршрута"),
        company_id: int | None = Query(None, description="ID компании"),
        start_point_id: int | None = Query(None, description="ID точки отправления"),
        end_point_id: int | None = Query(None, description="ID точки назначения"),
        container_id: int | None = Query(None, description="ID контейнера"),
        effective_from: str | None = Query(None, description="Начало периода (YYYY-MM-DD) или (DD.MM.YYYY)"),
        effective_to: str | None = Query(None, description="Конец периода (YYYY-MM-DD) или (DD.MM.YYYY)"),
    ):
        d_from = None
        d_to = None
        try:
            if effective_from:
                d_from = self._parse_date(effective_from)
            if effective_to:
                d_to = self._parse_date(effective_to)
        except ValueError as e:
            raise HTTPException(status_code=400, detail=str(e))

        return await self._get_filtered_routes_helper(
            page=page,
            limit=limit,
            route_type=route_type,
            company_id=company_id,
            start_point_id=start_point_id,
            end_point_id=end_point_id,
            container_id=container_id,
            date_from=d_from,
            date_to=d_to
        )

    async def add_route(self, route_to_add: AddRouteRequest = Body(...)):
        try:
            date_from = self._parse_date(route_to_add.effective_from)
            date_to = self._parse_date(route_to_add.effective_to)
        except ValueError as e:
            raise HTTPException(status_code=400, detail=str(e))

        if route_to_add.route_type == "rail":
            if not hasattr(route_to_add.price, 'price'):
                raise HTTPException(
                    status_code=400,
                    detail="Invalid price structure for 'rail'. Expected: price, drop, guard."
                )
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
        elif route_to_add.route_type == "sea":
            if not hasattr(route_to_add.price, 'filo') and not hasattr(route_to_add.price, 'fifo'):
                raise HTTPException(
                    status_code=400,
                    detail="Invalid price structure for 'sea'. Expected: filo, fifo."
                )
            new_route = SeaRouteModel(
                company_id=route_to_add.company_id,
                container_id=route_to_add.container_id,
                start_point_id=route_to_add.start_point_id,
                end_point_id=route_to_add.end_point_id,
                effective_from=date_from,
                effective_to=date_to,
                filo=getattr(route_to_add.price, 'filo', None),
                fifo=getattr(route_to_add.price, 'fifo', None),
            )
        else:
            raise HTTPException(status_code=400, detail=f"Unknown route_type: {route_to_add.route_type}")

        async with database.session() as session:
            try:
                session.add(new_route)
                await session.flush()

                route_class = RailRouteModel if route_to_add.route_type == "rail" else SeaRouteModel

                temp = await session.execute(
                    select(route_class).where(route_class.id == new_route.id).options(
                        joinedload(route_class.container),
                        joinedload(route_class.company),
                        joinedload(route_class.start_point),
                        joinedload(route_class.end_point),
                    )
                )
                joined_res = temp.scalar()
            except InvalidRequestError as e:
                raise HTTPException(status_code=400, detail=str(e))
            except Exception as e:
                raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

        result = self._parse_route_to_schema(joined_res, route_to_add.route_type)

        return {
            "status": "OK",
            "new_route": result,
        }

    async def edit_route(self, edit_route: EditRouteRequest = Body(...)):
        is_rail = edit_route.edit_params.route_type == "rail"
        is_sea = edit_route.edit_params.route_type == "sea"

        if is_rail:
            route_class = RailRouteModel
        elif is_sea:
            route_class = SeaRouteModel
        else:
            raise HTTPException(status_code=400, detail=f"Incorrect route type '{edit_route.edit_params.route_type}'")

        correct_route_id = await self._exe_q(
            select(route_class.id).where(route_class.id == edit_route.route_id),
            return_scalar=True
        )

        if not correct_route_id:
            raise HTTPException(status_code=404, detail=f"Incorrect route id '{edit_route.route_id}'")

        route_with_current_dates = await self._exe_q(
            select(route_class).where(route_class.id == edit_route.route_id),
            return_scalar=True
        )

        current_date_from = route_with_current_dates.effective_from.date()
        current_date_to = route_with_current_dates.effective_to.date()

        try:
            date_from = self._parse_date(
                edit_route.edit_params.effective_from) if edit_route.edit_params.effective_from else datetime.fromtimestamp(0).date()
            date_to = self._parse_date(
                edit_route.edit_params.effective_to) if edit_route.edit_params.effective_to else datetime.fromtimestamp(10000000000).date()
        except ValueError as e:
            raise HTTPException(status_code=400, detail=str(e))

        update_values = {}
        fields_to_check = ['effective_from', 'effective_to',
                           'container_id', 'company_id', 'start_point_id', 'end_point_id']

        for field in fields_to_check:
            value = getattr(edit_route.edit_params, field, None)
            if value:
                if field == 'effective_from':
                    req_to = edit_route.edit_params.effective_to
                    actual_to = date_to if req_to else current_date_to

                    if date_from > actual_to:
                        raise HTTPException(
                            status_code=400,
                            detail=f"Effective From ({date_from}) cannot be after Effective To ({actual_to})"
                        )
                    update_values[field] = date_from
                    continue

                if field == 'effective_to':
                    req_from = edit_route.edit_params.effective_from
                    actual_from = date_from if req_from else current_date_from

                    if date_to < actual_from:
                        raise HTTPException(
                            status_code=400,
                            detail=f"Effective To ({date_to}) cannot be before Effective From ({actual_from})"
                        )
                    update_values[field] = date_to
                    continue

                update_values[field] = value

        rail_price = ['price', 'drop', 'guard']
        sea_price = ['filo', 'fifo']

        if is_rail and edit_route.edit_params.price:
            for field in rail_price:
                value = getattr(edit_route.edit_params.price, field, None)
                if value is not None:
                    update_values[field] = value
        elif is_sea and edit_route.edit_params.price:
            for field in sea_price:
                value = getattr(edit_route.edit_params.price, field, None)
                if value is not None:
                    update_values[field] = value

        if update_values:
            edit_stmt = update(route_class).where(route_class.id == edit_route.route_id).values(**update_values)
            async with database.session() as session:
                await session.execute(edit_stmt)

        route_to_change = await self._exe_q(
            select(route_class).where(route_class.id == edit_route.route_id).options(
                joinedload(route_class.container),
                joinedload(route_class.company),
                joinedload(route_class.start_point),
                joinedload(route_class.end_point),
            ),
            return_scalar=True
        )

        result = self._parse_route_to_schema(route_to_change, "rail" if is_rail else "sea")

        return {
            "status": "OK",
            "changed_route": result,
        }

    async def delete_routes(self, ids_dict: DeleteRoutesRequest = Body(...)):
        async with database.session() as session:
            count_sea, count_rail = 0, 0

            if ids_dict.sea:
                sea_count_stmt = select(func.count(SeaRouteModel.id)).where(SeaRouteModel.id.in_(ids_dict.sea))
                res = await session.execute(sea_count_stmt)
                count_sea = res.scalar() or 0
                await session.execute(delete(SeaRouteModel).where(SeaRouteModel.id.in_(ids_dict.sea)))

            if ids_dict.rail:
                rail_count_stmt = select(func.count(RailRouteModel.id)).where(RailRouteModel.id.in_(ids_dict.rail))
                res = await session.execute(rail_count_stmt)
                count_rail = res.scalar() or 0
                await session.execute(delete(RailRouteModel).where(RailRouteModel.id.in_(ids_dict.rail)))

        return {
            "status": "OK",
            "deleted_routes": count_sea + count_rail,
        }


crud = RouteCRUD
