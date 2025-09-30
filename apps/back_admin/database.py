import os
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from typing import Any

from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import DeclarativeBase


async def exe_q(q, return_scalar=False):
    async with database.session() as session:
        temp = await session.execute(q)
        return temp.scalar() if return_scalar else temp.scalars().all()


class Base(DeclarativeBase):
    __table_args__: dict[str, Any] | tuple[Any] = {
        "mysql_default_charset": os.getenv("DB_CHARSET", "utf8mb4"),
        "mysql_collate": os.getenv("DB_COLLATE", "utf8mb4_unicode_ci"),
    }


def _build_db_url():
    required = ["DB_SCHEME", "DB_HOST"]
    if any(not os.getenv(var) for var in required):
        raise ValueError(f"Missing required env vars: {required}")

    scheme = os.getenv("DB_SCHEME")
    user = os.getenv("DB_USER")
    password = os.getenv("DB_PASS")
    host = os.getenv("DB_HOST")
    port = os.getenv("DB_PORT", "3306")
    name = os.getenv("DB_NAME", "")

    return f"{scheme}://{user}:{password}@{host}:{port}/{name}"


class Database:
    _engine: AsyncEngine = None
    _sessionmaker: async_sessionmaker | None = None

    async def init(self):
        db_url = _build_db_url()
        self._engine = create_async_engine(
            db_url,
            echo=True,
            pool_pre_ping=True,
        )
        self._sessionmaker = async_sessionmaker(
            self._engine,
            expire_on_commit=False,
            class_=AsyncSession,
        )

        async with self._engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)

    @asynccontextmanager
    async def session(self) -> AsyncGenerator:
        if not self._sessionmaker:
            await self.init()

        if not self._sessionmaker:
            raise Exception("No sessionmaker")

        async with self._sessionmaker() as session:
            try:
                yield session
                await session.commit()
            except Exception:
                await session.rollback()
                raise
            finally:
                await session.close()


database = Database()
