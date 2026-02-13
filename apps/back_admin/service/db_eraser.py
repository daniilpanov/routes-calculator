import aiomysql
from shared.config import get_settings


async def clear_database_data():
    settings = get_settings()
    pool = await aiomysql.create_pool(
        host=settings.DB_HOST,
        user=settings.DB_USER,
        password=settings.DB_PASS,
        db=settings.DB_NAME,
    )

    async with pool.acquire() as conn:
        async with conn.cursor() as cursor:
            await cursor.execute("SET FOREIGN_KEY_CHECKS = 0")

            await cursor.execute("SHOW TABLES")
            tables = [row[0] for row in await cursor.fetchall()]

            for table in tables:
                await cursor.execute(f"DELETE FROM `{table}`")

            for table in tables:
                try:
                    await cursor.execute(f"ALTER TABLE `{table}` AUTO_INCREMENT = 1")
                except:
                    pass

            await cursor.execute("SET FOREIGN_KEY_CHECKS = 1")
            await conn.commit()

    pool.close()
    await pool.wait_closed()
