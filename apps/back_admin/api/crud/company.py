from fastapi import Body, Path
from fastapi.params import Param

from back_admin.api.abstract_crud import AbstractCRUD
from back_admin.models import CompanyModel
from pydantic import BaseModel


class CompanyInstanceSchemaNoId(BaseModel):
    name: str


class CompanyInstanceSchema(CompanyInstanceSchemaNoId):
    id: int | None = None  # noqa: A003


class CompanyCRUD(AbstractCRUD):
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
        self._router.add_api_route("/", self.get_all, methods=["GET"], response_model=list[CompanyInstanceSchema])
        self._router.add_api_route(
            "/", self.create,
            methods=["POST"],
            response_model=CompanyInstanceSchema,
            status_code=201,
        )
        self._router.add_api_route("/{id}", self.get_by_id, methods=["GET"], response_model=CompanyInstanceSchema)
        self._router.add_api_route("/{id}", self.edit, methods=["PUT"], response_model=CompanyInstanceSchema)
        self._router.add_api_route("/{id}", self.delete, methods=["DELETE"], response_model=CompanyInstanceSchema)
        self._router.add_api_route("/count", self.count, methods=["GET"], response_model=int)
        self._router.add_api_route("/find-one", self.find_one, methods=["GET"], response_model=CompanyInstanceSchema)
        self._router.add_api_route("/find-many", self.find_many, methods=["GET"], response_model=CompanyInstanceSchema)

    async def count(self) -> int:
        return await self._count()

    async def get_all(
        self,
        offset: int = Param(default=0),
        limit: int | None = Param(default=None),
    ) -> list[CompanyInstanceSchema]:
        return await self._get_all(offset, limit)

    async def get_by_id(self, _id: int = Path()) -> CompanyInstanceSchema:
        return await self._get_by_id(_id)

    async def create(self, data: CompanyInstanceSchemaNoId = Body()) -> CompanyInstanceSchema:
        return await self._create(self.orm_model_class(**data.model_dump()))

    async def edit(self, _id: int = Path(), data: CompanyInstanceSchemaNoId = Body()) -> CompanyInstanceSchemaNoId:
        return await self._edit(_id, data)

    async def delete(self, _id: int = Path()):
        return await self._delete(_id)

    async def delete_many(self, _ids: list[int] = Body()):
        return await self._delete_many(_ids)

    async def find_one(self, filters: CompanyInstanceSchemaNoId = Param()) -> CompanyInstanceSchema:
        return await self._find_one(**filters.model_dump(exclude_unset=True))

    async def find_many(self, filters: CompanyInstanceSchemaNoId = Param()) -> list[CompanyInstanceSchema]:
        return await self._find_many(**filters.model_dump(exclude_unset=True))


crud = CompanyCRUD
