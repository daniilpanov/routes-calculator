from unittest.mock import patch

import pytest
from backend_user.services.get_rates import get_rates


class MockCurrency:
    def __init__(self, code, value):
        self.code = code
        self.value = value


class MockExchangeRates:
    def __init__(self, date):
        self.rates = [
            MockCurrency("USD", 90.0),
            MockCurrency("EUR", 100.0),
            MockCurrency("CNY", 12.5),
        ]


def test_get_rates_returns_dict():
    with patch("backend_user.services.get_rates.ExchangeRates", return_value=MockExchangeRates(None)):
        rates = get_rates()

    assert isinstance(rates, dict)
    assert rates["USD"] == 90.0
    assert rates["EUR"] == 100.0
    assert rates["RUB"] == 1.0
    assert rates["RUR"] == 1.0


def test_get_rates_cached_same_day():
    with patch("backend_user.services.get_rates.ExchangeRates", return_value=MockExchangeRates(None)):
        rates1 = get_rates()
        rates2 = get_rates()

    assert rates1 is rates2


def test_get_rates_with_passed_datetime():
    import datetime

    dt = datetime.datetime(2024, 6, 15, 12, 0, 0)
    with patch("backend_user.services.get_rates.ExchangeRates", return_value=MockExchangeRates(None)):
        rates = get_rates(dt)

    assert isinstance(rates, dict)


def test_get_rates_api_failure_raises():
    import datetime

    with (
        patch("backend_user.services.get_rates.ExchangeRates", side_effect=ConnectionError("API unavailable")),
        pytest.raises(ConnectionError),
    ):
        get_rates(datetime.datetime(2020, 1, 1))
