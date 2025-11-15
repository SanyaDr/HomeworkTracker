from fastapi import FastAPI, Request
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse

app = FastAPI(title="Homework Tracker", version="0.0.1")
app.mount("/static", StaticFiles(directory="frontend/static"), name="static")
templates = Jinja2Templates(directory="frontend/templates")

# TODO async def ??
# @app.get("/")
# def read_root():
#     return {"message": "Добро пожаловать в Трекер домашних заданий!"}

@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/api/assignments/")
def get_assignments():
    # Пока это тестовые данные - потом заменим на реальные
    return [
        {"id": 1, "subject": "Математика", "title": "Проект по алгебре", "status": "active"},
        {"id": 2, "subject": "Информатика", "title": "Написать API", "status": "completed"}
    ]