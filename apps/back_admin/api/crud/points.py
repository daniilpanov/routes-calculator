import re

from fastapi import Body, HTTPException, Query

from back_admin.api.abstract_crud import AbstractCRUD
from back_admin.database import database
from back_admin.models import PointModel
from back_admin.models.requests.point import AddPointModelRequest, EditPointRequest
from pydantic import BaseModel
from sqlalchemy import delete, func, or_, select, update
from sqlalchemy.exc import IntegrityError


class PointInstanceSchema(BaseModel):
    id: int  # noqa: A003
    city: str
    country: str
    RU_city: str | None = None
    RU_country: str | None = None


class PointCRUD(AbstractCRUD):
    def __init__(self):
        super().__init__()
        self._router.tags = ["points-admin"]

    @property
    def orm_model_class(self):
        return PointModel

    @property
    def instance_schema_class(self):
        return PointInstanceSchema

    @property
    def prefix(self) -> str:
        return "points"

    def _initialize_routes(self):
        self._router.prefix = "/points"

        self._router.add_api_route("/{point_name}", self.find_point_by_name, methods=["GET"])
        self._router.add_api_route("/", self.get_points_compat, methods=["GET"])
        self._router.add_api_route("/", self.add_point_compat, methods=["POST"])
        self._router.add_api_route("/{point_id}", self.edit_point_compat, methods=["PUT"])
        self._router.add_api_route("/{point_id}", self.delete_points_compat, methods=["DELETE"])

    @staticmethod
    def is_cyrillic(text: str) -> bool:
        return bool(re.search('[а-яА-Я]', text))

    async def find_point_by_name(self, search_txt: str = Query(..., description="Название точки")):
        stmt = select(PointModel)

        if self.is_cyrillic(search_txt):
            stmt = stmt.where(
                or_(
                    PointModel.RU_city.ilike(f"%{search_txt}%"),
                    PointModel.RU_country.ilike(f"%{search_txt}%"),
                )
            )
        else:
            stmt = stmt.where(
                or_(
                    PointModel.city.ilike(f"%{search_txt}%"),
                    PointModel.country.ilike(f"%{search_txt}%"),
                )
            )

        async with database.session() as session:
            point_name = (await session.execute(stmt)).scalars().all()

        return {
            "status": "OK",
            "point_name": point_name,
        }

    async def get_points_compat(
        self,
        page: int = Query(1, ge=1, description="Номер страницы"),
        limit: int = Query(25, ge=1, description="Количество элементов на странице")
    ):

        offset = (page - 1) * limit

        async with database.session() as session:
            stmt = select(PointModel)
            points = (await session.execute(stmt)).scalars().all()

            total_count = len(points)
            result = points[offset: offset + limit]

        return {
            "status": "OK",
            "count": total_count,
            "points": result,
        }

    async def add_point_compat(self, point: AddPointModelRequest = Body(...)):
        try:
            async with database.session() as session:
                new_point = PointModel(
                    city=point.city,
                    country=point.country,
                    RU_city=point.RU_city,
                    RU_country=point.RU_country,
                )
                session.add(new_point)
                await session.flush()
                await session.refresh(new_point)
                res = self.instance_schema_class.model_validate(new_point.dict())
        except IntegrityError:
            raise HTTPException(
                status_code=400,
                detail="Already exist."
            )

        return {
            "status": "OK",
            "new_point": res,
        }

    async def edit_point_compat(self, edit_point: EditPointRequest = Body(...)):
        point_stmt = update(PointModel).where(PointModel.id == edit_point.point_id)

        update_values = {}
        fields_to_check = ['RU_city', 'RU_country', 'city', 'country']

        for field in fields_to_check:
            value = getattr(edit_point, field, None)
            if value:
                update_values[field] = value

        if update_values:
            point_stmt = point_stmt.values(**update_values)

        async with database.session() as session:
            await session.execute(point_stmt)

            point_to_change = await session.get(PointModel, edit_point.point_id)
            if not point_to_change:
                raise HTTPException(status_code=404, detail="Point not found")

            res = self.instance_schema_class.model_validate(point_to_change.dict())

        return {
            "status": "OK",
            "point": res,
        }

    async def delete_points_compat(
        self,
        points_id: list[int] = Query(..., description="Список точек для удаления (ID)")
    ):
        if not points_id:
            return {
                "status": "OK",
                "removed_count": 0,
            }

        points_delete_stmt = delete(PointModel).where(PointModel.id.in_(points_id))
        points_count_stmt = select(func.count(PointModel.id)).where(PointModel.id.in_(points_id))

        async with database.session() as session:
            removed_count = (await session.execute(points_count_stmt)).scalar()
            try:
                await session.execute(points_delete_stmt)
            except IntegrityError:
                raise HTTPException(
                    status_code=403,
                    detail="Cannot delete point which is already in some routes",
                )

        return {
            "status": "OK",
            "removed_count": removed_count,
        }


crud = PointCRUD
