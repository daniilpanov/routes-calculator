from pydantic import BaseModel


class UploaderFieldsConfig(BaseModel):
    route_type: str = "_route_type"

    start_point: str
    end_point: str
    terminal: str

    effective_from: str
    effective_to: str

    container_transfer_terms: str
    container_shipment_terms: str
    container_condition: str

    service: str
    comment: str
    is_through: str

    conversation_percents: str
    sea_20dc: str
    sea_20dc_currency: str
    sea_40hc: str
    sea_40hc_currency: str
    rail_20dc24t: str
    rail_20dc24t_currency: str
    rail_20dc28t: str
    rail_20dc28t_currency: str
    rail_40hc: str
    rail_40hc_currency: str
