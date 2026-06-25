import asyncio
import json
import logging

from module_shared.database import get_database
from module_shared.models.setting import SettingItem, parse_setting_value
from module_shared.redis_client import get_redis
from module_shared.repositories.setting import get_setting as _get_setting
from module_shared.schemas.setting import SettingModel
from module_shared.setting_definitions import get_setting_definitions
from sqlalchemy import select

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


async def ensure_settings() -> None:
    definitions = get_setting_definitions()
    async with get_database().session_context() as session:
        for defn in definitions:
            result = await session.execute(
                select(SettingModel).where(
                    SettingModel.group == defn.group,
                    SettingModel.name == defn.name,
                ),
            )
            model = result.scalar_one_or_none()
            if model is not None:
                await _sync_locked(session, model, defn)
                continue
            model = SettingModel(
                group=defn.group,
                name=defn.name,
                description=defn.description,
                value_type=defn.value_type,
                value=defn.default,
                locked=defn.locked,
            )
            session.add(model)
            await session.flush()
            item = SettingItem.from_model(model)
            await set_settings_cache(item)
            logger.info("Created default setting: %s:%s = %s", defn.group, defn.name, defn.default)


async def _sync_locked(session, model, defn) -> None:
    changed = False
    if not model.locked and defn.locked:
        model.locked = True
        changed = True
    if model.value_type != defn.value_type:
        logger.warning(
            "Syncing value_type for %s:%s: %s -> %s",
            defn.group, defn.name, model.value_type, defn.value_type,
        )
        model.value_type = defn.value_type
        changed = True
    if model.value is None and defn.default is not None:
        try:
            parse_setting_value(defn.default, model.value_type)
            model.value = defn.default
            changed = True
        except (ValueError, TypeError):
            logger.warning("Cannot convert default for %s:%s", defn.group, defn.name)
    if changed:
        await session.flush()
        item = SettingItem.from_model(model)
        await set_settings_cache(item)
