from importlib.util import find_spec

from fastapi import FastAPI
from starlette.requests import Request
from starlette.responses import JSONResponse

from back_admin.autodiscover import api_discover
from back_admin.config import get_settings
from back_admin.jwt_middleware import JWTAuthMiddleware
from fastapi_another_jwt_auth import AuthJWT
from fastapi_another_jwt_auth.exceptions import AuthJWTException

if find_spec("dotenv") is not None:
    from dotenv import load_dotenv

    load_dotenv()

app = FastAPI()

# Configure AuthJWT with settings
AuthJWT.load_config(get_settings)


# Exception handler for JWT errors
@app.exception_handler(AuthJWTException)
def authjwt_exception_handler(request: Request, exc: AuthJWTException):
    return JSONResponse(status_code=exc.status_code, content={"detail": exc.message})


# Add JWT middleware to all routes
app.add_middleware(JWTAuthMiddleware)

routers = api_discover()
for router in routers:
    app.include_router(router)
