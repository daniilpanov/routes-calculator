from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession


async def clear_database_data(session: AsyncSession):
    await session.execute(text("SET FOREIGN_KEY_CHECKS = 0"))

    tables_descriptor = (await session.execute(text("SHOW TABLES"))).scalars()

    for table in tables_descriptor:
        if table != "alembic_version":
            await session.execute(text(f"DELETE FROM `{table}`"))

    await session.execute(text("SET FOREIGN_KEY_CHECKS = 1"))
