from .models.container import ContainerModel
from src.database import database


async def get_containers():
    async with database.session() as session:
        res = await session.query(ContainerModel).sort(ContainerModel.size)
    return res.all()


def search_container_ids(containers: list[ContainerModel], size: int):
    return [container for container in containers if container.size >= size]
