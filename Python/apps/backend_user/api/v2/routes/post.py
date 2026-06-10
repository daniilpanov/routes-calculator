from typing import Annotated

from fastapi import APIRouter, Depends

from backend_user.dependencies.auth_context import AuthContext, get_auth_context
from backend_user.schemas.form_requests import CalculateFormRequest
from backend_user.services.route_calculation import calculate_routes

router = APIRouter(prefix="/v2/routes", tags=["v2", "routes"])


@router.post("/calculate")
async def calculate(
    request: CalculateFormRequest,
    auth: Annotated[AuthContext, Depends(get_auth_context)],
):
    return await calculate_routes(request, auth)
