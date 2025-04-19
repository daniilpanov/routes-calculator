import datetime

from pydantic import BaseModel


class CalculateFormRequest(BaseModel):
    dispatchDate: datetime.date
    departureId: str
    destinationId: str
    cargoWeight: int
    containerType: int
    currency: str
