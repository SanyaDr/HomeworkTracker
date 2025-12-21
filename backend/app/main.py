# backend/app/main
import os

from fastapi import FastAPI, Request, Depends
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse
from fastapi.exceptions import HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

from app.api.endpoints import api_routers, frontend_routers
from app.core import init_db
from app.core import logger
from app.core import config as cfg
from app.core.config import publicPaths

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
static_dir = os.path.join(FRONTEND_DIR, "static")
if os.path.exists(static_dir):
    app.mount("/static", StaticFiles(directory=static_dir), name="static")
else:
    # Fallback на статику в backend/frontend
    backend_static_dir = os.path.join(BASE_DIR, "frontend", "static")
    if os.path.exists(backend_static_dir):
        app.mount("/static", StaticFiles(directory=backend_static_dir), name="static")

# Настраиваем Jinja2 шаблоны
templates_dir = os.path.join(FRONTEND_DIR, "templates")
if os.path.exists(templates_dir):
    templates = Jinja2Templates(directory=templates_dir)
else:
    # Fallback на шаблоны в backend/frontend
    backend_templates_dir = os.path.join(BASE_DIR, "frontend", "templates")
    if os.path.exists(backend_templates_dir):
        templates = Jinja2Templates(directory=backend_templates_dir)
    else:
        templates = None

app.state.templates = templates

# Инициализация базы данных при запуске
@app.on_event("startup")
def startup_event():
    init_db()
    try:
        from app.core.logger import cleanup_old_logs
        cleanup_old_logs(days_to_keep=cfg.DAYS_TO_KEEP_LOGS)
        print("Очистка старых логов выполнена")
    except Exception as e:
        print(f"Ошибка при очистке логов: {e}")

@app.middleware("http")
async def auth_middleware(request: Request, call_next):
    try:
        response = await call_next(request)

        excludedPaths = cfg.publicPaths
        if any(request.url.path.startswith(path) for path in excludedPaths):
            return response

        # Если 401 ошибка и это не API запрос - перенаправляем на логин
        if response.status_code == 401 and not request.url.path.startswith("/api/"):
            return RedirectResponse(url="/login")

        return response

    except HTTPException as exc:
        if exc.status_code == 401 and not request.url.path.startswith("/api/"):
            return RedirectResponse(url="/login")
        raise exc

# ==================== СБРОС ПАРОЛЯ ==========================
@app.get("/reset-password")
async def reset_password_page(request: Request, token: str = None):
    """Страница сброса пароля"""
    return templates.TemplateResponse(
        "resetPassword.html",
        {"request": request, "token": token}
    )

# ==================== ОБРАБОТЧИКИ ОШИБОК ====================

# Создайте функцию для обработки ошибок
@app.exception_handler(404)
async def not_found_handler(request: Request, exc):
    templates = request.app.state.templates
    if templates:
        return templates.TemplateResponse(
            "/errors/404.html",
            {"request": request},
            status_code=404
        )
    return JSONResponse(
        status_code=404,
        content={"detail": "Not Found"}
    )

@app.exception_handler(500)
async def server_error_handler(request: Request, exc):
    templates = request.app.state.templates
    if templates:
        return templates.TemplateResponse(
            "errors/500.html",
            {"request": request},
            status_code=500
        )
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal Server Error"}
    )

# # Для отлавливания всех исключений
@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    logger.log_error(exc, f"Запрос: {request.method} {request.url.path}")

    templates = request.app.state.templates
    if templates:
        # Передаем информацию об ошибке в шаблон
        import traceback
        error_info = {
            "error": str(exc),
            "trace": traceback.format_exc()
        }
        return templates.TemplateResponse(
            "errors/500.html",
            {
                "request": request,
                "error_info": error_info
            },
            status_code=500
        )

    return JSONResponse(
        status_code=500,
        content={
            "detail": "Internal Server Error",
            "error": str(exc)
        }
    )
