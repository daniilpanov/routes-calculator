from datetime import date, datetime
from typing import Any

from fastapi import Body, HTTPException, Query
from pydantic import BaseModel, ConfigDict, field_validator
from sqlalchemy import delete, func, select, update
from sqlalchemy.exc import IntegrityError, InvalidRequestError
from sqlalchemy.orm import joinedload

from back_admin.api.abstract_crud import AbstractCRUD
from back_admin.database import database
from back_admin.models import DropModel
from back_admin.models.requests.drop import (
    AddDropRequest,
    DeleteDropRequest,
    EditDropRequest,
)


class NestedCompanySchema(BaseModel):
    id: int
    name: str
    model_config = ConfigDict(from_attributes=True)


class NestedContainerSchema(BaseModel):
    id: int
    name: str
    size: int
    type: str
    weight_from: float
    weight_to: float
    model_config = ConfigDict(from_attributes=True)


class NestedPointSchema(BaseModel):
    id: int
    city: str
    country: str
    RU_city: str | None = None
    RU_country: str | None = None
    model_config = ConfigDict(from_attributes=True)


class DropResponseSchema(BaseModel):
    id: int  # noqa: A003
    company: NestedCompanySchema
    container: NestedContainerSchema
    sea_start_point: NestedPointSchema | None
    sea_end_point: NestedPointSchema | None
    rail_start_point: NestedPointSchema | None
    rail_end_point: NestedPointSchema | None
    start_date: int
    end_date: int
    price: float
    currency: str

    model_config = ConfigDict(from_attributes=True)

    @field_validator("start_date", "end_date", mode="before")
    @classmethod
    def date_to_timestamp(cls, v: Any) -> int:
        if isinstance(v, (date, datetime)):
            return int(datetime.combine(v, datetime.min.time()).timestamp())
        return v


class DropListResponse(BaseModel):
    status: str
    count: int
    drops: list[DropResponseSchema]


class DropCRUD(AbstractCRUD):
    def __init__(self):
        super().__init__()
        self._router.tags = ["drop-admin"]

    @property
    def prefix(self) -> str:
        return "drop"

    @property
    def orm_model_class(self):
        return DropModel

    @property
    def instance_schema_class(self):
        return DropResponseSchema

    def _initialize_routes(self):
        self._router.prefix = "/drop"

        self._router.add_api_route("/", self.get_drops, methods=["GET"])
        self._router.add_api_route("/", self.add_drop, methods=["POST"])
        self._router.add_api_route("/{drop_id}", self.edit_drop, methods=["PUT"])
        self._router.add_api_route("/", self.delete_drops, methods=["DELETE"])

    @staticmethod
    async def _exe_q(q, return_scalar=False):
        async with database.session() as session:
            temp = await session.execute(q)
            return temp.scalar() if return_scalar else temp.scalars().all()

    @staticmethod
    def _ts_to_date(ts: int | None) -> date | None:
        if ts is None:
            return None
        try:
            return datetime.fromtimestamp(ts).date()
        except (ValueError, OSError, OverflowError):
            raise HTTPException(status_code=400, detail=f"Invalid timestamp: {ts}")

    async def _get_filtered_drops_helper(
        self,
        page: int,
        limit: int,
        company_id: int | None = None,
        container_id: int | None = None,
        sea_start_point_id: int | None = None,
        sea_end_point_id: int | None = None,
        rail_start_point_id: int | None = None,
        rail_end_point_id: int | None = None,
        date_from: date | None = None,
        date_to: date | None = None,
    ) -> dict:
        offset = (page - 1) * limit

        stmt = select(DropModel).options(
            joinedload(DropModel.container),
            joinedload(DropModel.company),
            joinedload(DropModel.sea_start_point),
            joinedload(DropModel.sea_end_point),
            joinedload(DropModel.rail_start_point),
            joinedload(DropModel.rail_end_point),
        )

        if company_id:
            stmt = stmt.where(DropModel.company_id == company_id)
        if container_id:
            stmt = stmt.where(DropModel.container_id == container_id)

        if sea_start_point_id:
            stmt = stmt.where(DropModel.sea_start_point_id == sea_start_point_id)
        if sea_end_point_id:
            stmt = stmt.where(DropModel.sea_end_point_id == sea_end_point_id)
        if rail_start_point_id:
            stmt = stmt.where(DropModel.rail_start_point_id == rail_start_point_id)
        if rail_end_point_id:
            stmt = stmt.where(DropModel.rail_end_point_id == rail_end_point_id)

        if date_from:
            stmt = stmt.where(DropModel.end_date >= date_from)
        if date_to:
            stmt = stmt.where(DropModel.start_date <= date_to)

        count_stmt = select(func.count(DropModel.id))
        if company_id:
            count_stmt = count_stmt.where(DropModel.company_id == company_id)
        if container_id:
            count_stmt = count_stmt.where(DropModel.container_id == container_id)
        if sea_start_point_id:
            count_stmt = count_stmt.where(
                DropModel.sea_start_point_id == sea_start_point_id
            )
        if sea_end_point_id:
            count_stmt = count_stmt.where(
                DropModel.sea_end_point_id == sea_end_point_id
            )
        if rail_start_point_id:
            count_stmt = count_stmt.where(
                DropModel.rail_start_point_id == rail_start_point_id
            )
        if rail_end_point_id:
            count_stmt = count_stmt.where(
                DropModel.rail_end_point_id == rail_end_point_id
            )
        if date_from:
            count_stmt = count_stmt.where(DropModel.end_date >= date_from)
        if date_to:
            count_stmt = count_stmt.where(DropModel.start_date <= date_to)

        async with database.session() as session:
            total_count = (await session.execute(count_stmt)).scalar()

            stmt = stmt.order_by(DropModel.id.desc()).offset(offset).limit(limit)
            items_orm = (await session.execute(stmt)).scalars().all()

            items = [
                self.instance_schema_class.model_validate(item) for item in items_orm
            ]

        return {
            "status": "OK",
            "count": total_count,
            "drops": items,
        }

    async def get_drops(
        self,
        page: int = Query(1, ge=1, description="Номер страницы"),
        limit: int = Query(25, ge=1, description="Количество элементов"),
        company_id: int | None = Query(None, description="ID компании"),
        container_id: int | None = Query(None, description="ID контейнера"),
        sea_start_point_id: int | None = Query(None),
        sea_end_point_id: int | None = Query(None),
        rail_start_point_id: int | None = Query(None),
        rail_end_point_id: int | None = Query(None),
        effective_from: int | None = Query(
            None, description="Начало периода (Timestamp)"
        ),
        effective_to: int | None = Query(None, description="Конец периода (Timestamp)"),
    ):
        d_from = self._ts_to_date(effective_from)
        d_to = self._ts_to_date(effective_to)

        return await self._get_filtered_drops_helper(
            page=page,
            limit=limit,
            company_id=company_id,
            container_id=container_id,
            sea_start_point_id=sea_start_point_id,
            sea_end_point_id=sea_end_point_id,
            rail_start_point_id=rail_start_point_id,
            rail_end_point_id=rail_end_point_id,
            date_from=d_from,
            date_to=d_to,
        )

    async def add_drop(self, drop_data: AddDropRequest = Body(...)):
        start_date = self._ts_to_date(drop_data.start_date)
        end_date = self._ts_to_date(drop_data.end_date)

        if start_date > end_date:
            raise HTTPException(
                status_code=400, detail="Start date cannot be after End date"
            )

        new_drop = DropModel(
            company_id=drop_data.company_id,
            container_id=drop_data.container_id,
            sea_start_point_id=drop_data.sea_start_point_id,
            sea_end_point_id=drop_data.sea_end_point_id,
            rail_start_point_id=drop_data.rail_start_point_id,
            rail_end_point_id=drop_data.rail_end_point_id,
            start_date=start_date,
            end_date=end_date,
            price=drop_data.price,
            currency=drop_data.currency,
        )

        async with database.session() as session:
            try:
                session.add(new_drop)
                await session.flush()

                stmt = (
                    select(DropModel)
                    .where(DropModel.id == new_drop.id)
                    .options(
                        joinedload(DropModel.container),
                        joinedload(DropModel.company),
                        joinedload(DropModel.sea_start_point),
                        joinedload(DropModel.sea_end_point),
                        joinedload(DropModel.rail_start_point),
                        joinedload(DropModel.rail_end_point),
                    )
                )
                created_orm = (await session.execute(stmt)).scalar()

            except IntegrityError as e:
                if "1452" in str(e.orig):
                    raise HTTPException(
                        status_code=400,
                        detail="One of the provided IDs (company, container, or point) does not exist.",
                    )
                raise HTTPException(
                    status_code=400, detail=f"Database integrity error: {str(e)}"
                )
            except InvalidRequestError as e:
                raise HTTPException(status_code=400, detail=str(e))
            except Exception as e:
                raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

        result = self.instance_schema_class.model_validate(created_orm)

        return {
            "status": "OK",
            "new_drop": result,
        }

    async def edit_drop(self, edit_req: EditDropRequest = Body(...)):
        stmt_get = select(DropModel).where(DropModel.id == edit_req.drop_id)
        current_drop = await self._exe_q(stmt_get, return_scalar=True)

        if not current_drop:
            raise HTTPException(
                status_code=404, detail=f"Drop with id '{edit_req.drop_id}' not found"
            )

        update_values = {}

        req_from = self._ts_to_date(edit_req.start_date)
        req_to = self._ts_to_date(edit_req.end_date)

        if req_from:
            update_values["start_date"] = req_from

        if req_to:
            update_values["end_date"] = req_to

        actual_from = req_from if req_from else current_drop.start_date
        actual_to = req_to if req_to else current_drop.end_date

        if isinstance(actual_from, datetime):
            actual_from = actual_from.date()
        if isinstance(actual_to, datetime):
            actual_to = actual_to.date()

        if actual_from > actual_to:
            raise HTTPException(
                status_code=400,
                detail=f"Start date ({actual_from}) cannot be after End date ({actual_to})",
            )

        fields_map = [
            "company_id",
            "container_id",
            "sea_start_point_id",
            "sea_end_point_id",
            "rail_start_point_id",
            "rail_end_point_id",
            "price",
            "currency",
        ]

        for field in fields_map:
            val = getattr(edit_req, field)
            if val is not None:
                update_values[field] = val

        if update_values:
            stmt_update = (
                update(DropModel)
                .where(DropModel.id == edit_req.drop_id)
                .values(**update_values)
            )
            async with database.session() as session:
                try:
                    await session.execute(stmt_update)
                except Exception as e:
                    raise HTTPException(
                        status_code=500, detail=f"Update failed: {str(e)}"
                    )

        stmt_final = (
            select(DropModel)
            .where(DropModel.id == edit_req.drop_id)
            .options(
                joinedload(DropModel.container),
                joinedload(DropModel.company),
                joinedload(DropModel.sea_start_point),
                joinedload(DropModel.sea_end_point),
                joinedload(DropModel.rail_start_point),
                joinedload(DropModel.rail_end_point),
            )
        )

        drop_final = await self._exe_q(stmt_final, return_scalar=True)
        result = self.instance_schema_class.model_validate(drop_final)

        return {
            "status": "OK",
            "changed_drop": result,
        }

    async def delete_drops(self, req: DeleteDropRequest = Body(...)):
        if not req.ids:
            return {"status": "OK", "deleted_count": 0}

        async with database.session() as session:
            count_stmt = select(func.count(DropModel.id)).where(
                DropModel.id.in_(req.ids)
            )
            count = (await session.execute(count_stmt)).scalar() or 0

            del_stmt = delete(DropModel).where(DropModel.id.in_(req.ids))
            await session.execute(del_stmt)

        return {
            "status": "OK",
            "deleted_count": count,
        }


crud = DropCRUD
