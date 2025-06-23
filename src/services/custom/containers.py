import datetime

from sqlalchemy import select

from .models.container import ContainerModel
from .mappers.containers import map_containers
from src.database import database
from src.mapper_decorator import apply_mapper


@apply_mapper(map_containers)
async def get_containers(date: datetime.date, departure_id: str, destination_id: str):
    async with database.session() as session:
        res = await session.execute(select(ContainerModel).order_by(ContainerModel.size))
    return res.scalars().all()


def search_container_ids(containers: list, weight: int, size: int):
    return [container['id'] for container in containers if container['size'] == size and container['weight_from'] <= weight <= container['weight_to']]
