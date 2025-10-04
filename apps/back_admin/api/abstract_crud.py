from abc import ABC, abstractmethod
from typing import TypeVar

from fastapi import APIRouter, HTTPException, status

from back_admin.database import Base, database
from pydantic import BaseModel
from sqlalchemy import delete, func, or_, select
from sqlalchemy.exc import IntegrityError

ORMModel = TypeVar("ORMModel", bound=Base)
InstanceSchema = TypeVar("InstanceSchema", bound=BaseModel)


class AbstractCRUD(ABC):
    def __init__(self):
        self._router = APIRouter()
        self._is_router_initialized = False

    @property
    @abstractmethod
    def prefix(self) -> str:
        pass

    @property
    def tags(self) -> list[str]:
        return [self.prefix, "crud"]

    @property
    @abstractmethod
    def orm_model_class(self) -> type[ORMModel]:
        pass

    @property
    @abstractmethod
    def instance_schema_class(self) -> type[InstanceSchema]:
        pass

    @abstractmethod
    def _initialize_routes(self):
        pass

    def get_router(self):
        if not self._is_router_initialized:
            self._initialize_routes()
            self._is_router_initialized = True

        return self._router

    async def _count(self) -> int:
        return await database.get_scalar(func.count(self.orm_model_class.id))

    async def _create(self, db_model: ORMModel):
        try:
            async with database.session() as sess:
                sess.add(db_model)
                await sess.flush()
                await sess.refresh(db_model)
                result = self.instance_schema_class.model_validate(db_model.dict())
        except IntegrityError:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=f"{self.prefix} already exists")

        return result

    async def _get_all(self, offset: int = 0, limit: int | None = None) -> list[InstanceSchema]:
        query = select(self.orm_model_class)

        if offset:
            query = query.offset(offset)
        if limit:
            query = query.limit(limit)

        result = database.get_all_scalars(query)
        return [self.instance_schema_class.model_validate(item.dict()) for item in result]

    async def _get_by_id(self, _id: int) -> InstanceSchema:
        async with database.session() as sess:
            model = await sess.get(self.orm_model_class, _id)

        if not model:
            raise HTTPException(status_code=404, detail=f"{self.prefix} not found")

        return self.instance_schema_class.model_validate(model.dict())

    async def _find_one(self, **filters) -> InstanceSchema:
        query = select(self.orm_model_class).where(or_(*[
            getattr(self.orm_model_class, col) == val
            for col, val in filters.items()
        ]))
        model = await database.get_scalar(query)

        if not model:
            raise HTTPException(status_code=404, detail=f"{self.prefix} not found")

        return self.instance_schema_class.model_validate(model.dict())

    async def _find_many(self, offset: int = 0, limit: int | None = None, **filters) -> list[InstanceSchema]:
        if filters:
            conditions = [
                getattr(self.orm_model_class, col) == val
                for col, val in filters.items()
            ]
            query = select(self.orm_model_class).where(or_(*conditions))
        else:
            query = select(self.orm_model_class)

        if offset:
            query = query.offset(offset)
        if limit:
            query = query.limit(limit)

        models = await database.get_all_scalars(query)

        return [self.instance_schema_class.model_validate(model.dict()) for model in models]

    async def _edit(self, _id: int, update_data: InstanceSchema) -> InstanceSchema:
        async with database.session() as sess:
            model = await sess.get(self.orm_model_class, _id)

            if not model:
                raise HTTPException(status_code=404, detail=f"{self.prefix} not found")

            update_dict = update_data.model_dump(exclude_unset=True)
            for field, value in update_dict.items():
                setattr(model, field, value)

            await sess.flush()
            await sess.refresh(model)

        return self.instance_schema_class.model_validate(model.dict())

    async def _delete(self, _id: int):
        async with database.session() as sess:
            model = await sess.get(self.orm_model_class, _id)
            if not model:
                raise HTTPException(status_code=404, detail=f"{self.prefix} not found")

            await sess.delete(model)

    async def _delete_many(self, _ids: list[int]):
        async with database.session() as sess:
            await sess.execute(delete(self.orm_model_class).where(self.orm_model_class.id.in_(_ids)))

    async def _search(
        self,
        column: str,
        value: str,
        offset: int = 0,
        limit: int | None = None,
    ) -> list[InstanceSchema]:
        """
        Records search by the one column using LIKE

        Args:
            column:
            value:
            offset:
            limit:
        """
        if not hasattr(self.orm_model_class, column):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Column '{column}' not found in {self.prefix}"
            )

        column_attr = getattr(self.orm_model_class, column)
        condition = column_attr.ilike(value)
        query = select(self.orm_model_class).where(condition)

        if offset:
            query = query.offset(offset)
        if limit:
            query = query.limit(limit)

        models = await database.get_all_scalars(query)
        return [self.instance_schema_class.model_validate(model.dict()) for model in models]

    async def _search_count(self, column: str, value: str) -> int:
        """
        A counter for records search by the one column using LIKE

        Args:
            column:
            value:
        """
        if not hasattr(self.orm_model_class, column):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Column '{column}' not found in {self.prefix}"
            )

        column_attr = getattr(self.orm_model_class, column)
        condition = column_attr.ilike(value)
        query = select(func.count(self.orm_model_class.id)).where(condition)

        return await database.get_scalar(query)
