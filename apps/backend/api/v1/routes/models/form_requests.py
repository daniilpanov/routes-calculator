import datetime
from typing import Any

from pydantic import BaseModel


class CalculateFormRequest(BaseModel):
    dispatchDate: datetime.date
    departureId: dict[str, Any]
    destinationId: dict[str, Any]
    cargoWeight: float
    containerType: int
    onlyInSelectedDateRange: bool = False
