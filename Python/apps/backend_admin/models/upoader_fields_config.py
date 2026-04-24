from pydantic import BaseModel


class UploaderFieldsConfig(BaseModel):
    # SERVICES
    column_name: str
    service_name: str
    description: str

    # ROUTES
    route_type: str = "_route_type"

    start_point: str
    end_point: str
    dropp_off_point: str
    terminal: str

    effective_from: str
    effective_to: str

    container_transfer_terms: str
    container_shipment_terms: str
    container_condition: str

    company: str
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
    drop20: str
    drop40: str

    # SERVICE PRICES
    # rail
    exp: str
    exp_currency: str
    de_creditation: str
    de_creditation_currency: str
    # sea
    dthc: str
    dthc_currency: str
    # all
    docs: str
    docs_currency: str
    release: str
    release_currency: str
    tao: str
    tao_currency: str
    prr: str
    prr_currency: str

    services: set[str] = {
        "exp",
        "de_creditation",
        "dthc",
        "docs",
        "release",
        "tao",
        "prr",
    }
