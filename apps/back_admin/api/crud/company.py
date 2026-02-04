from fastapi import Body, HTTPException, Path, Query

from back_admin.api.abstract_crud import AbstractCRUD
from back_admin.database import database
from back_admin.models import CompanyModel
from pydantic import BaseModel, ConfigDict
from sqlalchemy import delete, func, select, update
from sqlalchemy.exc import IntegrityError


class CompanyCreateSchema(BaseModel):
    name: str
    model_config = ConfigDict(from_attributes=True)


class CompanyEditSchema(BaseModel):
    company_id: int
    name: str | None = None
    model_config = ConfigDict(from_attributes=True)


class CompanyInstanceSchema(CompanyCreateSchema):
    id: int  # noqa: A003


class CompanyCRUD(AbstractCRUD):
    def __init__(self):
        super().__init__()
        self._router.tags = ["company-admin"]

    @property
    def orm_model_class(self):
        return CompanyModel

    @property
    def instance_schema_class(self):
        return CompanyInstanceSchema

    @property
    def prefix(self) -> str:
        return "company"

    def _initialize_routes(self):
        self._router.prefix = "/company"

        self._router.add_api_route("/", self.get_all_compat, methods=["GET"])
        self._router.add_api_route("/", self.create_compat, methods=["POST"])
        self._router.add_api_route("/{company_id}", self.edit_compat, methods=["PUT"])
        self._router.add_api_route("/{company_id}", self.delete_compat, methods=["DELETE"])
        self._router.add_api_route("/", self.delete_many_compat, methods=["DELETE"])

    async def get_all_compat(
        self,
        page: int = Query(1, ge=1, description="Номер страницы"),
        limit: int = Query(25, ge=1, description="Количество элементов на странице")
    ):
        offset = (page - 1) * limit

        async with database.session() as session:
            count_stmt = select(func.count(CompanyModel.id))
            total_count = (await session.execute(count_stmt)).scalar()

            stmt = select(CompanyModel).offset(offset).limit(limit)
            items_orm = (await session.execute(stmt)).scalars().all()

            items = [
                self.instance_schema_class.model_validate(item.dict())
                for item in items_orm
            ]

        return {
            "status": "OK",
            "count": total_count,
            "companies": items,
        }

    async def create_compat(self, data: CompanyCreateSchema = Body(...)):
        try:
            new_obj = await self._create(self.orm_model_class(**data.model_dump()))
        except HTTPException as e:
            raise e
        except Exception as e:
            raise HTTPException(status_code=400, detail=str(e))

        return {
            "status": "OK",
            "new_company": new_obj,
        }

    async def edit_compat(
        self,
        data: CompanyEditSchema = Body(...),
        company_id: int = Path(..., description="ID компании (из URL, игнорируется в пользу body)")
    ):
        target_id = data.company_id

        update_values = data.model_dump(exclude={'company_id'}, exclude_unset=True)

        if not update_values:
            return {"status": "OK", "company": None}

        async with database.session() as session:
            stmt = update(CompanyModel).where(CompanyModel.id == target_id).values(**update_values)
            await session.execute(stmt)

            updated_orm = await session.get(CompanyModel, target_id)
            if not updated_orm:
                raise HTTPException(status_code=404, detail="Company not found")

            updated_obj = self.instance_schema_class.model_validate(updated_orm.dict())

        return {
            "status": "OK",
            "company": updated_obj,
        }

    async def delete_compat(self, company_id: int = Path(..., description="ID компании")):
        await self._delete(company_id)
        return {
            "status": "OK",
        }

    async def delete_many_compat(
        self,
        ids: list[int] = Body(..., description="Список ID для удаления")
    ):
        if not ids:
            return {"status": "OK", "removed_count": 0}

        async with database.session() as session:
            count_stmt = select(func.count(CompanyModel.id)).where(CompanyModel.id.in_(ids))
            to_remove_count = (await session.execute(count_stmt)).scalar()

            try:
                delete_stmt = delete(CompanyModel).where(CompanyModel.id.in_(ids))
                await session.execute(delete_stmt)
            except IntegrityError:
                raise HTTPException(
                    status_code=403,
                    detail="Cannot delete company which is used in routes"
                )

        return {
            "status": "OK",
            "removed_count": to_remove_count,
        }


crud = CompanyCRUD
