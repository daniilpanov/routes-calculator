from abc import ABC, abstractmethod
from typing import Any, Callable, TypeVar, Generic

from fastapi import APIRouter, HTTPException, status
from sqlalchemy.exc import IntegrityError

from back_admin.database import Base, database
from pydantic import BaseModel
from sqlalchemy import or_, select, delete

ORMModel = TypeVar("ORMModel", bound=Base)
InstanceSchema = TypeVar("InstanceSchema", bound=BaseModel)
CreateInstanceSchema = TypeVar("CreateInstanceSchema", bound=BaseModel)
UpdateInstanceSchema = TypeVar("UpdateInstanceSchema", bound=BaseModel)


class AbstractCRUD(Generic[ORMModel, InstanceSchema, CreateInstanceSchema, UpdateInstanceSchema], ABC):
    @property
    @abstractmethod
    def prefix(self) -> str:
        pass

    @property
    def tags(self) -> list[str]:
        return [self.prefix, "crud"]

    @property
    @abstractmethod
    def orm_model(self) -> type[ORMModel]:
        pass

    @property
    @abstractmethod
    def instance_schema(self) -> type[InstanceSchema]:
        pass

    @property
    @abstractmethod
    def create_instance_schema(self) -> type[CreateInstanceSchema]:
        pass

    @property
    @abstractmethod
    def update_instance_schema(self) -> type[UpdateInstanceSchema]:
        pass

    @property
    @abstractmethod
    def methods(self) -> dict[str, Callable]:
        pass

    @property
    def routes(self) -> list[dict[str, Any]]:
        return [
            {
                "path": "create",
                "method": "create",
                "http_method": "POST",
                "status_code": status.HTTP_201_CREATED,
                "summary": f"Create new {self.prefix}",
                "response_model": self.instance_schema,
            },
            {
                "path": "find/many",
                "method": "find_many",
                "http_method": "GET",
                "status_code": status.HTTP_200_OK,
                "summary": f"Find many {self.prefix}",
                "response_model": list[self.instance_schema],
            },
            {
                "path": "find/one",
                "method": "find_one",
                "http_method": "GET",
                "status_code": status.HTTP_200_OK,
                "summary": f"Find one {self.prefix}",
                "response_model": self.instance_schema,
            },
            {
                "path": "get",
                "method": "get_all",
                "http_method": "GET",
                "status_code": status.HTTP_200_OK,
                "summary": f"Get all {self.prefix}",
                "response_model": list[self.instance_schema],
            },
            {
                "path": "get/{_id}",
                "method": "get_by_id",
                "http_method": "GET",
                "status_code": status.HTTP_200_OK,
                "summary": f"Get {self.prefix} by ID",
                "response_model": self.instance_schema,
            },
            {
                "path": "edit/{_id}",
                "method": "edit",
                "http_method": "PATCH",
                "status_code": status.HTTP_200_OK,
                "summary": f"Update {self.prefix} by ID",
                "response_model": self.instance_schema,
            },
            {
                "path": "delete/many",
                "method": "delete_many",
                "http_method": "DELETE",
                "status_code": status.HTTP_204_NO_CONTENT,
                "summary": f"Delete {self.prefix} by ID",
            },
            {
                "path": "delete/{_id}",
                "method": "delete",
                "http_method": "DELETE",
                "status_code": status.HTTP_204_NO_CONTENT,
                "summary": f"Delete {self.prefix} by ID",
            },
        ]

    async def _create(self, model: CreateInstanceSchema) -> InstanceSchema:
        db_model = self.orm_model(**model.model_dump())

        try:
            async with database.session() as sess:
                sess.add(db_model)
                await sess.flush()
                await sess.refresh(db_model)
                result = self.instance_schema.model_validate(db_model.dict())
        except IntegrityError:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=f"{self.prefix} already exists")

        return result

    async def _get_all(self, offset: int = 0, limit: int | None = None) -> list[InstanceSchema]:
        async with database.session() as sess:
            query = select(self.orm_model)

            if offset:
                query = query.offset(offset)
            if limit:
                query = query.limit(limit)

            result = (await sess.execute(query)).scalars().all()
        print(result)
        return [self.instance_schema.model_validate(item.dict()) for item in result]

    async def _get_by_id(self, _id: int) -> InstanceSchema:
        async with database.session() as sess:
            model = await sess.get(self.orm_model, _id)

        if not model:
            raise HTTPException(status_code=404, detail=f"{self.prefix} not found")

        return self.instance_schema.model_validate(model.dict())

    async def _find_one(self, **filters) -> InstanceSchema:
        async with database.session() as sess:
            query = sess.query(self.orm_model).where(or_([
                getattr(self.orm_model, col) == val
                for col, val in filters.items()
            ]))
            model = await query.first()

        if not model:
            raise HTTPException(status_code=404, detail=f"{self.prefix} not found")

        return self.instance_schema.model_validate(model.dict())

    async def _find_many(self, offset: int = 0, limit: int | None = None, **filters) -> list[InstanceSchema]:
        async with database.session() as sess:
            if filters:
                conditions = [
                    getattr(self.orm_model, col) == val
                    for col, val in filters.items()
                ]
                query = sess.query(self.orm_model).where(or_(*conditions))
            else:
                query = sess.query(self.orm_model)

            if offset:
                query = query.offset(offset)
            if limit:
                query = query.limit(limit)

            models = await query.all()

        return [self.instance_schema.model_validate(model.dict()) for model in models]

    async def _edit(self, _id: int, update_data: UpdateInstanceSchema) -> InstanceSchema:
        async with database.session() as sess:
            model = await sess.get(self.orm_model, _id)

            if not model:
                raise HTTPException(status_code=404, detail=f"{self.prefix} not found")

            update_dict = update_data.model_dump(exclude_unset=True)
            for field, value in update_dict.items():
                setattr(model, field, value)

            await sess.flush()
            await sess.refresh(model)

        return self.instance_schema.model_validate(model.dict())

    async def _delete(self, _id: int):
        async with database.session() as sess:
            model = await sess.get(self.orm_model, _id)
            if not model:
                raise HTTPException(status_code=404, detail=f"{self.prefix} not found")

            await sess.delete(model)

    async def _delete_many(self, _ids: list[int]):
        async with database.session() as sess:
            await sess.execute(delete(self.orm_model).where(self.orm_model.id.in_(_ids)))

    def build_router(self) -> APIRouter:
        router = APIRouter(prefix="/" + self.prefix, tags=self.tags)

        for config in self.routes:
            full_path = f"/{config['path']}".rstrip("/")

            method = self.methods.get(config["method"])
            if not method:
                continue

            route_params = {
                "path": full_path,
                "endpoint": method,
                "methods": [config["http_method"]],
                "status_code": config["status_code"],
                "summary": config.get("summary", ""),
                "response_model": config.get("response_model"),
            }
            route_params = {k: v for k, v in route_params.items() if v is not None}
            router.add_api_route(**route_params)

        return router
