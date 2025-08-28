from pydantic import BaseModel


class AddContainerRequest(BaseModel):
    size: int
    weight_from: int
    weight_to: int
    name: str
    type: str


class EditContainerRequest(BaseModel):
    container_id: int
    size: int | None = None
    weight_from: int | None = None
    weight_to: int | None = None
    name: str | None = None
    type: str | None = None
