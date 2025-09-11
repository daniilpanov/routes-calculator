from pydantic import BaseModel


class SeaPrices(BaseModel):
    filo: float | None = None
    fifo: float | None = None


class RailPrices(BaseModel):
    price: int | None = None
    drop: int | None = None
    guard: int | None = None


class AddRouteRequest(BaseModel):
    company_id: int
    container_id: int
    start_point_id: int
    end_point_id: int
    effective_from: str
    effective_to: str
    price: RailPrices | SeaPrices


class FilterParams(BaseModel):
    start_point_id: int | None = None
    end_point_id: int | None = None
    company_id: int | None = None
    container_id: int | None = None
    effective_from: str | None = None
    effective_to: str | None = None
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
