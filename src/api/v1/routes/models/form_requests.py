import datetime
import json
from typing import Any

from pydantic import BaseModel, field_validator


class CalculateFormRequest(BaseModel):
    dispatchDate: datetime.date
    departureId: dict[str, Any]
    destinationId: dict[str, Any]
    cargoWeight: int
    containerType: int

    @field_validator("departureId", mode="before")
    def dep_convert(cls, points: str):
        return json.loads(points)

    @field_validator("destinationId", mode="before")
    def dest_convert(cls, points: str):
        return json.loads(points)
