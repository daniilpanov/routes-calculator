import datetime

from pydantic import BaseModel


class CalculateFormRequest(BaseModel):
    dispatchDate: datetime.date
    departure: str
    destination: str
    cargoWeight: int
    containerType: int
    currency: str
