import aiomysql
from shared.config import get_settings


async def create_db_dump():
    settings = get_settings()
    pool = await aiomysql.create_pool(
        host=settings.DB_HOST,
        user=settings.DB_USER,
        password=settings.DB_PASS,
        db=settings.DB_NAME,
    )
    res = ""

    async with pool.acquire() as conn:
        async with conn.cursor() as cursor:
            await cursor.execute("SHOW TABLES")
            tables = [row[0] for row in await cursor.fetchall()]

            for table in tables:
                await cursor.execute(f"SHOW CREATE TABLE `{table}`")
                create_sql = (await cursor.fetchone())[1].replace("CREATE TABLE ", "CREATE TABLE IF NOT EXISTS ", 1)
                res += f"{create_sql};\n\n"

                await cursor.execute(f"SELECT * FROM `{table}`")
                rows = await cursor.fetchall()

                if rows:
                    await cursor.execute(f"DESCRIBE `{table}`")
                    columns = [col[0] for col in await cursor.fetchall()]

                    values_list = []
                    for row in rows:
                        row_values = []
                        for value in row:
                            if value is None:
                                row_values.append("NULL")
                            elif isinstance(value, (int, float)):
                                row_values.append(str(value))
                            else:
                                escaped = str(value).replace("\\", "\\\\").replace("'", "''")
                                row_values.append(f"'{escaped}'")

                        values_list.append(f"({', '.join(row_values)})")

                    if values_list:
                        columns_str = ', '.join([f"`{col}`" for col in columns])
                        values_str = ',\n    '.join(values_list)
                        insert_sql = f"INSERT INTO `{table}` ({columns_str}) VALUES\n    {values_str};\n\n"
                        res += insert_sql

                res += "\n"

    pool.close()
    await pool.wait_closed()

    return res
