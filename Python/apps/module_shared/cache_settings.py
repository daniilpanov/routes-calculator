import asyncio
import json
import logging

from module_shared.models.setting import SettingItem
from module_shared.redis_client import get_redis
from module_shared.repositories.setting import get_setting as _get_setting

logger = logging.getLogger(__name__)

SETTINGS_CACHE_TTL = 43200  # 12 hours
SETTINGS_CACHE_PREFIX = "backend_user:settings"


def _settings_cache_key(group: str, name: str) -> str:
    return f"{SETTINGS_CACHE_PREFIX}:{group}:{name}"


async def get_setting_cached(session, group: str, name: str) -> SettingItem | None:
    key = _settings_cache_key(group, name)
    try:
        redis = get_redis()
        cached = await redis.get(key)
        if cached is not None:
            return SettingItem(**json.loads(cached))
    except Exception:
        logger.warning("Redis unavailable for settings, falling back to DB: %s:%s", group, name)

    item = await _get_setting(session, group, name)
    if item is not None:
        asyncio.create_task(set_settings_cache(item))
    return item


async def set_settings_cache(item: SettingItem) -> None:
    try:
        redis = get_redis()
        key = _settings_cache_key(item.group, item.name)
        data = item.model_dump(mode="json")
        await redis.set(key, json.dumps(data), ex=SETTINGS_CACHE_TTL)
        logger.debug("Settings cache set: %s", key)
    except Exception:
        logger.exception("Failed to set settings cache: %s:%s", item.group, item.name)


async def delete_settings_cache(group: str, name: str) -> None:
    key = _settings_cache_key(group, name)
    try:
        redis = get_redis()
        await redis.delete(key)
        logger.debug("Settings cache deleted: %s", key)
    except Exception:
        logger.exception("Failed to delete settings cache: %s", key)
