import datetime
from typing import Annotated

from fastapi import APIRouter, HTTPException
from fastapi.params import Depends
from fastapi.responses import StreamingResponse
from starlette.status import HTTP_200_OK, HTTP_500_INTERNAL_SERVER_ERROR

from back_admin.service.db_management.db_dumper import create_db_dump
from back_admin.service.db_management.db_eraser import clear_database_data
from shared.database import Database, get_database
from shared.responses import DetailErrorResponse, ErrorDescriptor
from shared.responses_fabric import create_an_error_descriptor_from_an_exception

router = APIRouter(prefix="/db")


@router.get("/data", status_code=200, response_class=StreamingResponse, responses={
    HTTP_200_OK: {
        "content": {"application/octet-stream": {}},
        "description": "Database SQL Dump",
        "headers": {
            "Content-Disposition": {
                "description": "attachment; filename=\"dump-<today>.sql\"",
                "schema": {"type": "string"},
            },
        },
    },
    HTTP_500_INTERNAL_SERVER_ERROR: {"model": DetailErrorResponse[ErrorDescriptor]},
})
async def make_db_dump(db: Annotated[Database, Depends(get_database)], structure: bool = True):
    async with db.session_context() as session:
        try:
            return StreamingResponse(
                create_db_dump(session, structure),
                headers={
                    "Content-Disposition": f"attachment; filename=\"dump-{datetime.date.today().isoformat()}.sql\"",
                },
            )
        except Exception as e:
            raise HTTPException(
                status_code=HTTP_500_INTERNAL_SERVER_ERROR,
                detail=create_an_error_descriptor_from_an_exception(e),
            ) from e


@router.delete("/data", status_code=204, responses={
    HTTP_500_INTERNAL_SERVER_ERROR: {"model": DetailErrorResponse[ErrorDescriptor]},
})
async def erase_all_data(db: Annotated[Database, Depends(get_database)]):
    async with db.session_context() as session:
        try:
            await clear_database_data(session)
        except Exception as e:
            raise HTTPException(
                status_code=HTTP_500_INTERNAL_SERVER_ERROR,
                detail=create_an_error_descriptor_from_an_exception(e),
            ) from e
