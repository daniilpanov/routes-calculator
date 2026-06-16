import datetime
import json
from unittest.mock import AsyncMock, patch

import pytest
from backend_user.services.get_rates import get_rates


class MockCurrency:
    def __init__(self, code, value):
        self.code = code
        self.value = value


class MockExchangeRates:
    def __init__(self, _date):
        self.rates = [
            MockCurrency("USD", 90.0),
            MockCurrency("EUR", 100.0),
            MockCurrency("CNY", 12.5),
        ]


def _mock_redis_client(get_return=None):
    from unittest.mock import MagicMock

    mock_redis = AsyncMock()
    mock_redis.get = AsyncMock(return_value=get_return)
    mock_redis.set = AsyncMock()
    mock_client = MagicMock()
    mock_client.client = mock_redis
    return mock_client


@pytest.mark.asyncio
async def test_get_rates_returns_tuple():
    client = _mock_redis_client()
    with (
        patch("backend_user.services.get_rates.ExchangeRates", return_value=MockExchangeRates(None)),
        patch("backend_user.services.get_rates.get_redis_client", return_value=client),
    ):
        rates, dt = await get_rates()

    assert isinstance(rates, dict)
    assert rates["USD"] == 90.0
    assert rates["EUR"] == 100.0
    assert rates["RUB"] == 1.0
    assert rates["RUR"] == 1.0
    assert dt == datetime.date.today()


@pytest.mark.asyncio
async def test_get_rates_with_passed_datetime():
    dt = datetime.datetime(2024, 6, 15, 12, 0, 0)
    client = _mock_redis_client()
    with (
        patch("backend_user.services.get_rates.ExchangeRates", return_value=MockExchangeRates(None)),
        patch("backend_user.services.get_rates.get_redis_client", return_value=client),
    ):
        rates, updated_at = await get_rates(dt)

    assert isinstance(rates, dict)
    assert updated_at == datetime.date(2024, 6, 15)


@pytest.mark.asyncio
async def test_get_rates_api_failure_fallback_to_redis():
    cached = json.dumps({"rates": {"USD": 85.0}, "date": "2024-06-14"})
    client = _mock_redis_client(get_return=cached)
    with (
        patch("backend_user.services.get_rates.ExchangeRates", side_effect=ConnectionError("API unavailable")),
        patch("backend_user.services.get_rates.get_redis_client", return_value=client),
    ):
        rates, cached_date = await get_rates(datetime.datetime(2020, 1, 1))

    assert rates["USD"] == 85.0
    assert cached_date == datetime.date(2024, 6, 14)


@pytest.mark.asyncio
async def test_get_rates_api_failure_no_cache_raises():
    client = _mock_redis_client()
    with (
        patch("backend_user.services.get_rates.ExchangeRates", side_effect=ConnectionError("API unavailable")),
        patch("backend_user.services.get_rates.get_redis_client", return_value=client),
        pytest.raises(RuntimeError, match="No rates available"),
    ):
        await get_rates(datetime.datetime(2020, 1, 1))
