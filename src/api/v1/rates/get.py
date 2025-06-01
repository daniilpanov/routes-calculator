import datetime
from functools import lru_cache

from fastapi import APIRouter

from pycbrf.toolbox import ExchangeRates

router = APIRouter(prefix='/v1/rates', tags=['rates'])


@lru_cache(1024)
@router.get('/')
def get_rates(dt_now: datetime.datetime = None):
    if dt_now is None:
        dt_now = datetime.datetime.now()
    rates = ExchangeRates(dt_now)
    return {currency.code: float(currency.value) for currency in rates.rates}