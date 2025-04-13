from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

app = FastAPI()
app.mount("/res", StaticFiles(directory="res"), name="res")
templates = Jinja2Templates(directory="html")

@app.get('/')
def home(request: Request):
    return templates.TemplateResponse('routes-calc-form.html', {'request': request})

@app.get('/calculate')
def home(request: Request):
    return templates.TemplateResponse('routes-calc-form.html', {'request': request, 'routes': []})
