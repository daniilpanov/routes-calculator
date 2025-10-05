from fastapi import APIRouter

from back_admin.database import database
from back_admin.models import ContainerModel
from back_admin.models.requests.container import AddContainerRequest, EditContainerRequest
from sqlalchemy import select, update

router = APIRouter(prefix="/container", tags=["container-admin"])

async def exe_q(q, return_scalar=False):
    async with database.session() as session:
        temp = await session.execute(q)
        return temp.scalar() if return_scalar else temp.scalars().all()


@router.post("")
async def getContainer():
    stmt = select(ContainerModel)
    containers = await exe_q(stmt)

    return {
        "status": "OK",
        "containers": containers,
    }


@router.put("/edit")
async def editContainer(edit_container: EditContainerRequest):
    container_stmt = update(
        ContainerModel,
    ).where(
        ContainerModel.id == edit_container.container_id,
    )

    if edit_container.size:
        container_stmt = container_stmt.values(
            size=edit_container.size,
        )
    if edit_container.weight_from:
        container_stmt = container_stmt.values(
            weight_from=edit_container.weight_from,
        )
    if edit_container.weight_to:
        container_stmt = container_stmt.values(
            weight_to=edit_container.weight_to,
        )
    if edit_container.type:
        container_stmt = container_stmt.values(
            type=edit_container.type,
        )

    async with database.session() as session:
        container_to_change = await session.execute(container_stmt)

    return {
        "status": "OK",
        "container": container_to_change,
    }


@router.post("/add")
async def addContainer(add_container: AddContainerRequest):
    new_container = ContainerModel(
        name=add_container.name,
        size=add_container.size,
        weight_from=add_container.weight_from,
        weight_to=add_container.weight_to,
        type=add_container.type,
    )
    async with database.session() as session:
        session.add(new_container)
        session.commit()

    return {
        "status": "OK",
        "new_container": new_container,
    }


@router.delete("/delete")
async def deleteContainer(container_id: int):
    container_delete_stmt = select(
        ContainerModel,
    ).where(
        ContainerModel.id == container_id,
    )
    async with database.session() as session:
        await session.delete(container_delete_stmt)
        session.commit()

    return {
        "status": "OK",
        "container_id": container_id,
    }
