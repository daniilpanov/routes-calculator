from typing import Annotated

from fastapi import APIRouter, Depends

from backend_user.dependencies.auth_context import AuthContext, get_auth_context
from module_shared.config import get_settings as get_shared_settings

router = APIRouter(prefix="/v2/demo", tags=["v2", "demo"])


@router.get("/feature-flags")
async def demo_feature_flags(auth: Annotated[AuthContext, Depends(get_auth_context)]):
    if auth.is_demo:
        excluded = get_shared_settings().DEMO_EXCLUDED_FIELDS
        return {"blurred_fields": list(excluded)}
    return {"blurred_fields": []}
