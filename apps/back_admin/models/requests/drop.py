from typing import Literal

from pydantic import BaseModel


class DropFilterParams(BaseModel):
    company_id: int | None = None
    container_id: int | None = None
    sea_start_point_id: int | None = None
    sea_end_point_id: int | None = None
    rail_start_point_id: int | None = None
    rail_end_point_id: int | None = None
    date_from: int | None = None
    date_to: int | None = None


class FilterDropRequest(BaseModel):
    page: int = 1
    limit: int = 25
    filter_fields: DropFilterParams


class AddDropRequest(BaseModel):
    company_id: int
    container_id: int
    sea_start_point_id: int | None = None
    sea_end_point_id: int | None = None
    rail_start_point_id: int | None = None
    rail_end_point_id: int | None = None
    start_date: int
    end_date: int
    price: float
    currency: str = "USD"


class EditDropRequest(BaseModel):
    drop_id: int
    company_id: int | None = None
    container_id: int | None = None
    sea_start_point_id: int | None = None
    sea_end_point_id: int | None = None
    rail_start_point_id: int | None = None
    rail_end_point_id: int | None = None
    start_date: int | None = None
    end_date: int | None = None
    price: float | None = None
    currency: str | None = None


class DeleteDropRequest(BaseModel):
    ids: list[int]
