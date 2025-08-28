from pydantic import BaseModel


class SeaPrices(BaseModel):
    filo: float | None = None
    fifo: float | None = None


class RailPrices(BaseModel):
    price: int | None = None
    drop: int | None = None
    guard: int | None = None


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
    effective_from: str | None = None
    effective_to: str | None = None
    company: str | None = None
    container: str | None = None
    route_type: str | None = None
    price: RailPrices | SeaPrices | None = None


class FilterRoutesRequest(BaseModel):
    page: int = 1
    limit: int = 25
    filter_fields: FilterParams


class DeleteManyRoutesRequest(BaseModel):
    rail: list[int]
    sea: list[int]


class EditRouteRequest(BaseModel):
    route_id: int
    other_params: FilterParams
