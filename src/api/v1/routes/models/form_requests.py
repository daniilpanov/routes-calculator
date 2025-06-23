import datetime
from typing import Any, Dict
import json

from pydantic import BaseModel, field_validator


class CalculateFormRequest(BaseModel):
    dispatchDate: datetime.date
    departureId: Dict[str, Any]
    destinationId: Dict[str, Any]
    cargoWeight: int
    containerType: int

    @field_validator('departureId', mode='before')
    def dep_convert(cls, points: str):
        return json.loads(points)

    @field_validator('destinationId', mode='before')
    def dest_convert(cls, points: str):
        return json.loads(points)
