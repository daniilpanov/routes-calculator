from pydantic import BaseModel


class SeaPrices(BaseModel):
    filo: float | None = None
    fifo: float | None = None


class RailPrices(BaseModel):
    price: int
    drop: int = 0
    guard: int | None = None


class AddRouteRequest(BaseModel):
    route_type: str
    company_id: int
    container_id: int
    start_point_id: int
    end_point_id: int
    effective_from: int
    effective_to: int
    price: RailPrices | SeaPrices


class FilterParams(BaseModel):
    start_point_id: int | None = None
    end_point_id: int | None = None
    company_id: int | None = None
    container_id: int | None = None
    effective_from: int | None = None
    effective_to: int | None = None
    route_type: str | None = None
    price: RailPrices | SeaPrices | None = None


class FilterRoutesRequest(BaseModel):
    page: int = 1
    limit: int = 25
    filter_fields: FilterParams


class DeleteRoutesRequest(BaseModel):
    rail: list[int] | None = None
    sea: list[int] | None = None


class EditRouteRequest(BaseModel):
    route_id: int
    edit_params: FilterParams
