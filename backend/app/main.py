from fastapi import FastAPI, Request
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse

app = FastAPI(title="Homework Tracker", version="0.0.1")
app.mount("/static", StaticFiles(directory="frontend/static"), name="static")
templates = Jinja2Templates(directory="frontend/templates")

# # Создаем таблицы при запуске приложения
# create_tables()

@app.get("/", response_class=HTMLResponse)
async def homePage(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

