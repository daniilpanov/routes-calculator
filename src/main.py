from importlib.util import find_spec

from src.autodiscover import api_discover

if find_spec("dotenv") is not None:
    from dotenv import load_dotenv

    load_dotenv()

from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

app = FastAPI()
app.mount("/res", StaticFiles(directory="res"), name="res")
app.mount("/lib", StaticFiles(directory="lib"), name="lib")
templates = Jinja2Templates(directory=".")

routers = api_discover()
for router in routers:
    app.include_router(router)


@app.get("/")
async def home(request: Request):
    return templates.TemplateResponse(
        "index.html",
        {
            "request": request,
        },
    )
