from fastapi import Body, HTTPException, Path

from back_admin.api.abstract_crud import AbstractCRUD
from back_admin.database import database
from back_admin.models import ContainerModel, ContainerType
from pydantic import BaseModel, ConfigDict, field_validator


class ContainerCreateSchema(BaseModel):
    name: str
    size: int
    weight_from: float
    weight_to: float
    type: str  # noqa: A003

    model_config = ConfigDict(from_attributes=True)

    @field_validator('type', mode='before')
    @classmethod
    def parse_enum(cls, v):
        if isinstance(v, ContainerType):
            return v.value
        return v


class ContainerUpdateSchema(BaseModel):
    name: str | None = None
    size: int | None = None
    weight_from: float | None = None
    weight_to: float | None = None
    type: str | None = None  # noqa: A003

    model_config = ConfigDict(from_attributes=True)


class ContainerInstanceSchema(ContainerCreateSchema):
    id: int  # noqa: A003


class ContainerEditSchemaCompat(ContainerUpdateSchema):
    container_id: int


class ContainerCRUD(AbstractCRUD):
    def __init__(self):
        super().__init__()
        self._router.tags = ["container-admin"]

    @property
    def orm_model_class(self):
        return ContainerModel

    @property
    def instance_schema_class(self):
        return ContainerInstanceSchema

    @property
    def prefix(self) -> str:
        return "container"

    def _initialize_routes(self):
        self._router.prefix = "/container"

        self._router.add_api_route("/", self.get_all_compat, methods=["GET"])
        self._router.add_api_route("/", self.create_compat, methods=["POST"])
        self._router.add_api_route("/{container_id}", self.edit_compat, methods=["PUT"])
        self._router.add_api_route("/{container_id}", self.delete_compat, methods=["DELETE"])

    async def get_all_compat(self):
        items = await self._get_all()
        return {
            "status": "OK",
            "containers": items,
        }

    async def create_compat(self, data: ContainerCreateSchema = Body()):
        data_dict = data.model_dump()

        if 'type' in data_dict and isinstance(data_dict['type'], str):
            try:
                data_dict['type'] = ContainerType(data_dict['type'])
            except ValueError:
                raise HTTPException(status_code=400, detail=f"Invalid container type: {data_dict['type']}")

        new_obj = await self._create(self.orm_model_class(**data_dict))

        return {
            "status": "OK",
            "new_container": new_obj,
        }

    async def edit_compat(self, data: ContainerEditSchemaCompat = Body()):
        dump = data.model_dump(exclude={'container_id'}, exclude_unset=True)

        if 'type' in dump and isinstance(dump['type'], str):
            try:
                dump['type'] = ContainerType(dump['type'])
            except ValueError:
                raise HTTPException(status_code=400, detail=f"Invalid container type: {dump['type']}")

        async with database.session() as sess:
            model = await sess.get(self.orm_model_class, data.container_id)
            if not model:
                raise HTTPException(status_code=404, detail=f"{self.prefix} not found")

            for field, value in dump.items():
                if value is not None:
                    setattr(model, field, value)

            await sess.flush()
            await sess.refresh(model)

            updated_obj = self.instance_schema_class.model_validate(model.dict())

        return {
            "status": "OK",
            "container": updated_obj,
        }

    async def delete_compat(self, container_id: int = Path(..., description="ID контейнера")):
        await self._delete(container_id)
        return {
            "status": "OK",
        }

    async def get_by_id(self, _id: int = Path()) -> ContainerInstanceSchema:
        return await self._get_by_id(_id)


crud = ContainerCRUD
