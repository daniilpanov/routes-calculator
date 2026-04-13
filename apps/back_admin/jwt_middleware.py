"""JWT Authorization Middleware for back_admin app."""

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse

import jwt
from back_admin.config import get_settings
from fastapi_another_jwt_auth.exceptions import AuthJWTException


class JWTAuthMiddleware(BaseHTTPMiddleware):
    """Middleware to check JWT token in all requests."""

    async def dispatch(self, request: Request, call_next):
        """Check JWT token and pass request if valid."""
        settings = get_settings()

        # Get token from cookies (configured in settings)
        access_token = request.cookies.get("access_token_cookie")

        if not access_token:
            return JSONResponse(
                status_code=400,
                content={"detail": "Missing JWT token"}
            )

        try:
            # Verify JWT token using the same settings as auth app
            jwt.decode(
                access_token,
                settings.authjwt_secret_key,
                algorithms=[settings.jwt_algorithm]
            )
            # Token is valid, continue with request
            return await call_next(request)
        except jwt.ExpiredSignatureError:
            return JSONResponse(
                status_code=401,
                content={"detail": "Token has expired"}
            )
        except jwt.InvalidTokenError:
            return JSONResponse(
                status_code=401,
                content={"detail": "Invalid token"}
            )
        except AuthJWTException as exc:
            return JSONResponse(
                status_code=exc.status_code,
                content={"detail": exc.message}
            )
        except Exception:
            return JSONResponse(
                status_code=500,
                content={"detail": "Unknown error"}
            )
