import datetime

from pydantic import BaseModel


class AddRailRouteRequest(BaseModel):
    company_id: int
    container_id: int
    start_point_id: int
    end_point_id: int
    effective_from: datetime.datetime
    effective_to: datetime.datetime
    price: int
    drop: int
    guard: int | None


class AddSeaRouteRequest(BaseModel):
    company_id: int
    container_id: int
    start_point_id: int
    end_point_id: int
    effective_from: datetime.datetime
    effective_to: datetime.datetime
    fifo: float | None
    filo: float | None
