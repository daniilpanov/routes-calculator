from abc import ABC, abstractmethod
from typing import Any, Generic, TypeVar

from fastapi import APIRouter, HTTPException, status

from pydantic import BaseModel
from sqlalchemy import or_

from .database import database

DatabaseModel = TypeVar("DatabaseModel")
FullModel = TypeVar("FullModel", bound=BaseModel)
UpdateModel = TypeVar("UpdateModel", bound=BaseModel)


class AbstractCRUD(Generic[DatabaseModel, FullModel, UpdateModel], ABC):
    @property
    @abstractmethod
    def suffix(self) -> str:
        pass

    @property
    @abstractmethod
    def database_model(self) -> type[DatabaseModel]:
        pass

    @property
    @abstractmethod
    def full_model(self) -> type[FullModel]:
        pass

    @property
    @abstractmethod
    def update_model(self) -> type[UpdateModel]:
        pass

    @property
    def routes(self) -> list[dict[str, Any]]:
        return [
            {
                "path": "",
                "method": self.create,
                "http_method": "POST",
                "status_code": status.HTTP_201_CREATED,
                "summary": f"Create new {self.suffix}",
                "response_model": self.full_model
            },
            {
                "path": "find/many",
                "method": self.find_many,
                "http_method": "GET",
                "status_code": 200,
                "summary": f"Find many {self.suffix}",
                "response_model": list[self.full_model]
            },
            {
                "path": "find/one",
                "method": self.find_one,
                "http_method": "GET",
                "status_code": 200,
                "summary": f"Find one {self.suffix}",
                "response_model": self.full_model
            },
            {
                "path": "{_id}",
                "method": self.get_by_id,
                "http_method": "GET",
                "status_code": 200,
                "summary": f"Get {self.suffix} by ID",
                "response_model": self.full_model
            },
            {
                "path": "{_id}",
                "method": self.edit,
                "http_method": "PATCH",
                "status_code": 200,
                "summary": f"Update {self.suffix} by ID",
                "response_model": self.full_model
            },
            {
                "path": "{_id}",
                "method": self.delete,
                "http_method": "DELETE",
                "status_code": 204,
                "summary": f"Delete {self.suffix} by ID"
            }
        ]

    async def create(self, model: FullModel) -> FullModel:
        db_model = self.database_model(**model.dict())
        async with database.session() as sess:
            sess.add(db_model)
            await sess.commit()
            await sess.refresh(db_model)
        return self.full_model.from_orm(db_model)

    async def get_by_id(self, _id: int) -> FullModel:
        async with database.session() as sess:
            model = await sess.get(self.database_model, _id)

        if not model:
            raise HTTPException(status_code=404, detail=f"{self.suffix} not found")

        return self.full_model.from_orm(model)

    async def find_one(self, **filters) -> FullModel | None:
        async with database.session() as sess:
            query = sess.query(self.database_model).filter_by(**filters)
            model = await query.first()

        if not model:
            return None

        return self.full_model.from_orm(model)

    async def find_many(self, **filters) -> list[FullModel]:
        async with database.session() as sess:
            if filters:
                conditions = [
                    getattr(self.database_model, col) == val
                    for col, val in filters.items()
                ]
                query = sess.query(self.database_model).filter(or_(*conditions))
            else:
                query = sess.query(self.database_model)

            models = await query.all()

        return [self.full_model.from_orm(model) for model in models]

    async def edit(self, _id: int, update_data: UpdateModel) -> FullModel:
        async with database.session() as sess:
            model = await sess.get(self.database_model, _id)

            if not model:
                raise HTTPException(status_code=404, detail=f"{self.suffix} not found")

            update_dict = update_data.dict(exclude_unset=True)
            for field, value in update_dict.items():
                setattr(model, field, value)

            await sess.commit()
            await sess.refresh(model)

        return self.full_model.from_orm(model)

    async def delete(self, _id: int) -> None:
        async with database.session() as sess:
            model = await sess.get(self.database_model, _id)
            if not model:
                raise HTTPException(status_code=404, detail=f"{self.suffix} not found")

            await sess.delete(model)
            await sess.commit()

    def apply_to_router(self, router: APIRouter) -> None:
        for config in self.routes:
            full_path = f"/{self.suffix}/{config['path']}".rstrip("/")

            route_params = {
                "path": full_path,
                "endpoint": config["method"],
                "methods": [config["http_method"]],
                "status_code": config["status_code"],
                "summary": config.get("summary", ""),
                "response_model": config.get("response_model"),
            }
            route_params = {k: v for k, v in route_params.items() if v is not None}
            router.add_api_route(**route_params)
