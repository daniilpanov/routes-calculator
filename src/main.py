import datetime

from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pycbrf.toolbox import ExchangeRates

from src.requests import CalculateFormRequest

app = FastAPI()
app.mount("/res", StaticFiles(directory="res"), name="res")
templates = Jinja2Templates(directory="html")


@app.get('/')
def home(request: Request):
    rates = ExchangeRates(datetime.datetime.now())
    parsed_rates = {currency.code: float(currency.value) for currency in rates.rates}
    return templates.TemplateResponse('routes-calc-form.html', {'request': request, 'rates': dict(parsed_rates)})


@app.post('/calculate')
def calculate(request: CalculateFormRequest):
    print(request.model_dump())
    return [
        {
            "dateFrom": "2025-01-01T00:00:00",
            "dateTo": "2025-01-31T00:00:00",
            "beginCond": "FI",
            "finishCond": "CY",
            "containers": [
                {
                    "id": "6e44ccc7-afb5-11ee-9727-005056958eb3",
                    "name": "40 фут, высокий (40’ HC) ≤ 28т",
                    "nameLatin": "40 ft, high cube (40’HC) ≤ 28t"
                }
            ],
            "owner": "COC",
            "segments": [
                {
                    "segmentOrder": 1,
                    "type": "sea",
                    "from": {
                        "id": "6157ac6f-df06-43df-9399-c5a4b94bd160",
                        "name": "Шанхай",
                        "nameLatin": "Shanghai",
                        "country": "КИТАЙ",
                        "countryLatin": "China"
                    },
                    "to": {
                        "id": "789ca030-a529-4237-85e7-8070212bd365",
                        "name": "Новороссийск",
                        "nameLatin": "Novorossiysk",
                        "country": "РОССИЯ",
                        "countryLatin": "The Russian Federation"
                    },
                    "price": [
                        {
                            "containerId": "6e44ccc7-afb5-11ee-9727-005056958eb3",
                            "sum": 7800,
                            "currency": "USD"
                        }
                    ]
                },
                {
                    "segmentOrder": 2,
                    "type": "rail",
                    "from": {
                        "id": "d8147a29-4dc9-4786-8ca6-7d9d1c848b05",
                        "name": "Новороссийск (Эксп.)",
                        "nameLatin": "Noworossijsk (eksp.)",
                        "country": "РОССИЯ",
                        "countryLatin": "The Russian Federation"
                    },
                    "to": {
                        "id": "b6e35205-3440-4021-b653-9ed34e25927d",
                        "name": "Белый Раст",
                        "nameLatin": "Belyj Rast",
                        "country": "РОССИЯ",
                        "countryLatin": "The Russian Federation"
                    },
                    "price": [
                        {
                            "containerId": "6e44ccc7-afb5-11ee-9727-005056958eb3",
                            "sum": 98460,
                            "currency": "RUB"
                        }
                    ]
                }
            ],
            "services": [
                {
                    "name": "DTHC в порту назначения",
                    "nameLatin": "Destination terminal handling charge (DTHC)",
                    "code": "DTHC",
                    "id": "30bc18d4fe4da97a24676518a93151c676da41ca",
                    "isRequired": True,
                    "checked": True,
                    "price": [
                        {
                            "containerId": "6e44ccc7-afb5-11ee-9727-005056958eb3",
                            "sum": 49600,
                            "currency": "RUB"
                        }
                    ]
                },
                {
                    "name": "Терминальный сбор (OTHC)",
                    "nameLatin": "Terminal handling (OTHC)",
                    "code": "OTHC",
                    "id": "05aa5c9a0947dd74508c83079ee9a5172b07e18f",
                    "isRequired": False,
                    "checked": False,
                    "price": [
                        {
                            "containerId": "6e44ccc7-afb5-11ee-9727-005056958eb3",
                            "sum": 170,
                            "currency": "USD"
                        }
                    ]
                },
                {
                    "name": "Охрана груза в пути следования",
                    "nameLatin": "Convoy fee",
                    "code": "CONVOY_1",
                    "id": "2da6474fd20c67a1435cf9c601fbf4e278bc0250",
                    "isRequired": False,
                    "checked": False,
                    "price": [
                        {
                            "containerId": "6e44ccc7-afb5-11ee-9727-005056958eb3",
                            "sum": 1971,
                            "currency": "RUB"
                        }
                    ]
                },
                {
                    "name": "Доставка автомобильным транспортом до пункта назначения",
                    "nameLatin": "DOOR delivery within city limits",
                    "code": "FOT_DDP",
                    "id": "fa05778be99057efe61fc4a1240c11930e0587b6",
                    "isRequired": False,
                    "checked": False,
                    "price": [
                        {
                            "containerId": "6e44ccc7-afb5-11ee-9727-005056958eb3",
                            "sum": 45500,
                            "currency": "RUB"
                        }
                    ]
                },
                {
                    "name": "Доставка автомобильным транспортом от железнодорожной станции",
                    "nameLatin": "DOOR delivery within city limits",
                    "code": "FOT_DDU",
                    "id": "9c296ba3bcec2898737cc21878e0aa81130e40e4",
                    "isRequired": False,
                    "checked": False,
                    "price": [
                        {
                            "containerId": "6e44ccc7-afb5-11ee-9727-005056958eb3",
                            "sum": 60000,
                            "currency": "RUB"
                        }
                    ]
                }
            ],
            "id": "e9ec6110a1903f1a54bcd8e8cd253455d235a2ee"
        }
    ]
