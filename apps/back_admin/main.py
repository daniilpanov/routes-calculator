from importlib.util import find_spec

from fastapi import FastAPI, Request
from starlette.responses import JSONResponse

from fastapi_another_jwt_auth import AuthJWT
from fastapi_another_jwt_auth.exceptions import AuthJWTException

from .auth_settings import settings
from .autodiscover import api_discover, crud_discover

if find_spec("dotenv") is not None:
    from dotenv import load_dotenv

    load_dotenv()

app = FastAPI()


@AuthJWT.load_config
def get_config():
    return settings


@app.exception_handler(AuthJWTException)
def authjwt_exception_handler(request: Request, exc: AuthJWTException):
    return JSONResponse(status_code=exc.status_code, content={"detail": exc.message})


@app.middleware("http")
async def auth_middleware(request: Request, call_next):
    try:
        AuthJWT(request).jwt_required()
    except AuthJWTException as e:
        return authjwt_exception_handler(request, e)

    return await call_next(request)


routers = api_discover()
routers.extend(crud_discover())
for router in routers:
    app.include_router(router)
