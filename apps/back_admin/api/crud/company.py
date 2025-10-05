from typing import Callable

from fastapi import Path, Body
from fastapi.params import Param
from pydantic import BaseModel

from back_admin.api.abstract_crud import AbstractCRUD, ORMModel
from back_admin.models import CompanyModel


class CreateUpdateCompanyInstanceSchema(BaseModel):
    name: str

class CompanyInstanceSchema(CreateUpdateCompanyInstanceSchema):
    id: int  # noqa: A003


class CompanyCRUD(AbstractCRUD[CompanyModel, CompanyInstanceSchema, CreateUpdateCompanyInstanceSchema, CreateUpdateCompanyInstanceSchema]):
    @property
    def methods(self) -> dict[str, Callable]:
        return {
            "get_all": self.get_all,
            "get_by_id": self.get_by_id,
            "create": self.create,
            "edit": self.edit,
            "delete_many": self.delete_many,
            "delete": self.delete,
        }

    @property
    def prefix(self) -> str:
        return "company"

    @property
    def orm_model(self) -> type[ORMModel]:
        return CompanyModel

    @property
    def instance_schema(self) -> type[CompanyInstanceSchema]:
        return CompanyInstanceSchema

    @property
    def create_instance_schema(self) -> type[CreateUpdateCompanyInstanceSchema]:
        return CreateUpdateCompanyInstanceSchema

    @property
    def update_instance_schema(self) -> type[CreateUpdateCompanyInstanceSchema]:
        return CreateUpdateCompanyInstanceSchema

    async def get_all(self, offset: int = Param(default=0), limit: int | None = Param(default=None)) -> list[CompanyInstanceSchema]:
        return await self._get_all(offset, limit)

    async def get_by_id(self, _id: int = Path()) -> CompanyInstanceSchema:
        return await self._get_by_id(_id)

    async def create(self, data: CreateUpdateCompanyInstanceSchema = Body()) -> CompanyInstanceSchema:
        return await self._create(data)

    async def edit(self, _id: int = Path(), data: CreateUpdateCompanyInstanceSchema = Body()) -> CompanyInstanceSchema:
        return await self._edit(_id, data)

    async def delete(self, _id: int = Path()):
        return await self._delete(_id)

    async def delete_many(self, _ids: list[int] = Body()):
        return await self._delete_many(_ids)


crud = CompanyCRUD()
