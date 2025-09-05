from pydantic import BaseModel


class AddPointModelRequest(BaseModel):
    city: str
    country: str
    RU_city: str
    RU_country: str
