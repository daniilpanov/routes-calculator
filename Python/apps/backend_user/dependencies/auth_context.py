from typing import Annotated

from fastapi import Depends

from fastapi_another_jwt_auth import AuthJWT
from pydantic import BaseModel

from ..config import Settings, get_settings
from .auth import request_auth


class AuthContext(BaseModel):
    pass


def get_auth_context(
    authorization: Annotated[AuthJWT, Depends()],
    settings: Annotated[Settings, Depends(get_settings)],
) -> AuthContext:
    request_auth(authorization, settings)

    return AuthContext()
