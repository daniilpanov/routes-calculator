from importlib.util import find_spec

from fastapi import FastAPI

from backend.autodiscover import api_discover

if find_spec("dotenv") is not None:
    from dotenv import load_dotenv

    load_dotenv()

app = FastAPI()

routers = api_discover()
for router in routers:
    app.include_router(router)
