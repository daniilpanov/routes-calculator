import datetime

from backend_user.mapper_decorator import apply_mapper
from module_shared.database import get_database
from module_shared.models import ContainerModel
from sqlalchemy import select

from .mappers.containers import map_containers


@apply_mapper(map_containers)
async def get_containers(date: datetime.date, departure_id: str, destination_id: str):
    async with get_database().session_context() as session:
        res = await session.execute(
            select(ContainerModel).order_by(ContainerModel.size)
        )
    return res.scalars().all()


def search_container_ids(containers: list, weight: int, size: int):
    return [
        container["id"]
        for container in containers
        if container["size"] == size
        and container["weight_from"] <= weight <= container["weight_to"]
    ]
