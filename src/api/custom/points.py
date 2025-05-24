from src.api.custom.models import PointModel
from src.database import database


async def get_points():
    async with database.session() as session:
        result = await session.query(PointModel)
    return result
