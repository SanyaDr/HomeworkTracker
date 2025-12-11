# backend/app/main
import os

from fastapi import FastAPI, Request, Depends
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

from app.api.endpoints import api_routers, frontend_routers
from app.core import init_db, get_db
from app import schemes
from datetime import datetime

app = FastAPI(
    version="0.0.2",
    title="Homework Tracker",
    description="Веб-приложение для отслеживания домашних заданий",
    docs_url="/api/docs",
    redoc_url="/api/redoc"
)

for router in api_routers:
    app.include_router(router, prefix="/api")
for router in frontend_routers:
    app.include_router(router)

# Настройка CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://127.0.0.1:8000", "http://localhost:8000"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"],
    allow_headers=["Content-Type", "Authorization", "Accept", "X-Requested-With"],
    max_age=600,  # Кэшировать preflight запросы на 10 минут
)

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__))) #backend/
PROJECT_DIR = os.path.dirname(BASE_DIR)     # Корень проекта
FRONTEND_DIR = os.path.join(PROJECT_DIR, "frontend")

# Подключим статические файлы
static_dir = os.path.join(FRONTEND_DIR, "/static")
if os.path.exists(static_dir):
    app.mount("/static", StaticFiles(directory=static_dir), name="static")
else:
    # Fallback на статику в backend/frontend
    backend_static_dir = os.path.join(BASE_DIR, "frontend", "static")
    if os.path.exists(backend_static_dir):
        app.mount("/static", StaticFiles(directory=backend_static_dir), name="static")

# app.mount("/static", StaticFiles(directory="frontend/static"), name="static")
# Настраиваем Jinja2 шаблоны
templates_dir = os.path.join(FRONTEND_DIR, "templates")
print("Trying load templates from:", templates_dir)
if os.path.exists(templates_dir):
    templates = Jinja2Templates(directory=templates_dir)
    print(f"Templates loaded from: {templates_dir}")
else:
    # Fallback на шаблоны в backend/frontend
    backend_templates_dir = os.path.join(BASE_DIR, "frontend", "templates")
    if os.path.exists(backend_templates_dir):
        templates = Jinja2Templates(directory=backend_templates_dir)
        print(f"Templates loaded from: {backend_templates_dir}")
    else:
        templates = None
        print("Warning: Templates directory not found")

app.state.templates = templates

# Инициализация базы данных при запуске
@app.on_event("startup")
def startup_event():
    print("Инициализация базы данных...")
    init_db()
    print("База данных проинициализирована!")

# @app.get("/", response_class=HTMLResponse)
# async def homePage(request: Request):
#     return templates.TemplateResponse("index.html", {"request": request})


# ==================== API ЭНДПОИНТЫ ====================
#
# @app.get("/api/health")
# async def health_check(db: Session = Depends(get_db)):
#     """
#     Проверка здоровья приложения
#     """
#     try:
#         db.execute("SELECT 1")
#         db_status = "connected"
#     except Exception as e:
#         db_status = f"error: {str(e)}"
#
#     return JSONResponse({
#         "status": "healthy",
#         "service": "task-tracker",
#         "database": db_status,
#         "timestamp": datetime.utcnow().isoformat(),
#         "version": "1.0.0"
#     })

# ==================== СБРОС ПАРОЛЯ ==========================
@app.get("/reset-password")
async def reset_password_page(request: Request, token: str = None):
    """Страница сброса пароля"""
    return templates.TemplateResponse(
        "resetPassword.html",
        {"request": request, "token": token}
    )

# ==================== ОБРАБОТЧИКИ ОШИБОК ====================

@app.exception_handler(404)
async def not_found_exception_handler(request: Request, exc):
    """
    Обработка 404 ошибок
    """
    if request.url.path.startswith("/api/"):
        return JSONResponse(
            status_code=404,
            content={"detail": "Not Found", "path": request.url.path}
        )

    # Для фронтенда возвращаем JSON с информацией об ошибке
    # или можно создать специальный шаблон для 404
    # TODO добавь ту фотку с телеги
    return JSONResponse(
        status_code=404,
        content={
            "error": "Page not found",
            "path": request.url.path,
            "suggestions": ["Go to home page", "Check the URL"]
        }
    )

