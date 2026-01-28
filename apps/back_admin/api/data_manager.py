from io import BytesIO

from fastapi import APIRouter
from fastapi.responses import StreamingResponse

from back_admin.service.db_dumper import create_db_dump
from back_admin.service.db_eraser import clear_database_data

router = APIRouter(prefix="/data")


@router.get("/make-db-dump")
async def make_db_dump():
    return StreamingResponse(
        BytesIO((await create_db_dump()).encode("utf-8")),
        headers={"Content-Disposition": "attachment; filename=\"dump.sql\""},
    )


@router.delete("/")
async def erase_all_data():
    await clear_database_data()
