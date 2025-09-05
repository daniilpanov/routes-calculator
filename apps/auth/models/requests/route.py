import datetime

from pydantic import BaseModel


class SeaPrices(BaseModel):
    filo: float | None
    fifo: float | None


class RailPrices(BaseModel):
    price: int
    drop: int
    guard: int | None


class AddRouteRequest(BaseModel):
    company: str
    container: str
    start_point_name: str
    end_point_name: str
    effective_from: str
    effective_to: str
    price: RailPrices | SeaPrices


class FilterParams(BaseModel):
    start_point: str | None = None
    end_point: str | None = None
    effective_from: datetime.date | None = None
    effective_to: datetime.date | None = None
    company: str | None = None
    container: str | None = None


class FilterRoutesRequest(BaseModel):
    page: int = 1
    limit: int = 25
    filter_fields: FilterParams
