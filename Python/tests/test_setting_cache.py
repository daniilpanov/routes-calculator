import json
from unittest.mock import AsyncMock, patch

import pytest
from module_shared.cache_settings import get_setting_cached
from module_shared.models.setting import SettingItem
from module_shared.schemas.setting import SettingModel, SettingType


def _mock_redis(get_return=None):
    mock_redis = AsyncMock()
    mock_redis.get = AsyncMock(return_value=get_return)
    mock_redis.set = AsyncMock()
    mock_redis.delete = AsyncMock()
    return mock_redis


def _mock_setting(**overrides) -> SettingItem:
    data = {
        "id": 1, "group": "test_group", "name": "test_key",
        "description": None, "value_type": SettingType.STRING, "value": "test_val",
    }
    data.update(overrides)
    return SettingItem(**data)


@pytest.mark.asyncio
async def test_get_setting_cached_cache_hit():
    setting = _mock_setting()
    cached = json.dumps(setting.model_dump(mode="json"))
    redis = _mock_redis(get_return=cached)

    with patch("module_shared.cache_settings.get_redis", return_value=redis):
        result = await get_setting_cached(None, "test_group", "test_key")

    assert result is not None
    assert result.group == "test_group"
    assert result.name == "test_key"
    assert result.value == "test_val"


@pytest.mark.asyncio
async def test_get_setting_cached_cache_miss_db_found(sqlite_session):
    setting = SettingModel(group="test_group", name="test_key", value_type=SettingType.STRING, value="test_val")
    sqlite_session.add(setting)
    await sqlite_session.commit()

    redis = _mock_redis()

    with patch("module_shared.cache_settings.get_redis", return_value=redis):
        result = await get_setting_cached(sqlite_session, "test_group", "test_key")

    assert result is not None
    assert result.group == "test_group"
    assert result.name == "test_key"
    assert result.value == "test_val"


@pytest.mark.asyncio
async def test_get_setting_cached_not_found(sqlite_session):
    redis = _mock_redis()

    with patch("module_shared.cache_settings.get_redis", return_value=redis):
        result = await get_setting_cached(sqlite_session, "nonexistent", "key")

    assert result is None
