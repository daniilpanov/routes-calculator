from pydantic import BaseModel


class AddPointModelRequest(BaseModel):
    city: str
    country: str
    RU_city: str
    RU_country: str


class EditPointRequest(BaseModel):
    point_id: int
    city: str | None = None
    country: str | None = None
    RU_city: str | None = None
    RU_country: str | None = None


class FilterPointRequest(BaseModel):
    page: int = 1
    limit: int = 25
