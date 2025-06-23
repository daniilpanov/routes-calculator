from typing import Optional
from contextlib import asynccontextmanager
from sqlalchemy.ext.asyncio import create_async_engine, AsyncEngine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase
import os

from typing_extensions import AsyncGenerator


class Base(DeclarativeBase):
    __table_args__ = {
        'mysql_default_charset': os.getenv('DB_CHARSET', 'utf8mb4'),
        'mysql_collate': os.getenv('DB_COLLATE', 'utf8mb4_unicode_ci'),
    }


def _build_db_url():
    required = ['DB_SCHEME', 'DB_HOST']
    if any(not os.getenv(var) for var in required):
        raise ValueError(f'Missing required env vars: {required}')

    scheme = os.getenv('DB_SCHEME')
    user = os.getenv('DB_USER')
    password = os.getenv('DB_PASS')
    host = os.getenv('DB_HOST')
    port = os.getenv('DB_PORT', '3306')
    name = os.getenv('DB_NAME', '')

    return f'{scheme}://{user}:{password}@{host}:{port}/{name}'


class Database:
    _engine: AsyncEngine = None
    _sessionmaker: Optional[async_sessionmaker] = None

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
    async def session(self) -> AsyncGenerator[AsyncSession]:
        if not self._sessionmaker:
            await self.init()

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
