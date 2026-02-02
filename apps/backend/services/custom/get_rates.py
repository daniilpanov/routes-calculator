import datetime

from pycbrf.toolbox import ExchangeRates

_rates: dict[str, float] = {}
_last_update = None


def get_rates(dt_now: datetime.datetime | None = None):
    global _rates, _last_update

    if dt_now is None:
        dt_now = datetime.datetime.now()

    if dt_now.date() == _last_update:
        return _rates

    rates = ExchangeRates(dt_now)
    _rates = {currency.code: float(currency.value) for currency in rates.rates}
    _last_update = dt_now.date()
    return _rates
