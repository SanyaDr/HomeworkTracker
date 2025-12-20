from fastapi import APIRouter, Request, Depends
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
import os

from ... import schemes
from ...crud import tasks as crud_tasks
from ...crud import subjects as crud_subjects
from ...core import get_db
from ...core.config import getServerTime
from ...core.auth import get_current_user
from ...core.templates import get_templates

router = APIRouter(tags=["frontend"])


@router.get("/", response_class=HTMLResponse)
async def home_page(request: Request, templates = Depends(get_templates)):
    """
    Главная страница приложения
    """

    context = {
        "request": request,
        "current_year": getServerTime().year
    }
    return templates.TemplateResponse("index.html", context)


@router.get("/login", response_class=HTMLResponse)
async def login_page(request: Request, templates = Depends(get_templates)):
    """
    Страница входа
    """

    context = {
        "request": request,
        "current_year": getServerTime().year
    }
    return templates.TemplateResponse("login.html", context)


@router.get("/register", response_class=HTMLResponse)
async def register_page(request: Request , templates = Depends(get_templates)):
    """
    Страница регистрации
    """

    context = {
        "request": request,
        "current_year": getServerTime().year
    }
    return templates.TemplateResponse("register.html", context)


@router.get("/dashboard", response_class=HTMLResponse)
async def dashboard_page(
        request: Request,
        db: Session = Depends(get_db),
        current_user: schemes.UserResponse = Depends(get_current_user),
        templates = Depends(get_templates)
):
    """
    Панель управления (требует аутентификации)
    """
    # Получаем статистику для отображения на дашборде
    stats = crud_tasks.get_user_tasks_stats(db, current_user.id)

    # Получаем ближайшие дедлайны
    from app.schemes import TaskFilter
    filters = TaskFilter(limit=5, skip=0)
    upcoming_tasks, _ = crud_tasks.get_tasks(
        db,
        current_user.id,
        filters,
        include_overdue=True # Тут было False
    )

    context = {
        "request": request,
        "user": current_user,
        "stats": stats,
        "upcoming_tasks": upcoming_tasks,
        "current_year": getServerTime().year
    }

    return templates.TemplateResponse("dashboard.html", context)


@router.get("/tasks", response_class=HTMLResponse)
async def tasks_page(
        request: Request,
        db: Session = Depends(get_db),
        current_user: schemes.UserResponse = Depends(get_current_user),
        templates = Depends(get_templates)
):
    """
    Страница управления задачами
    """

    context = {
        "request": request,
        "user": current_user,
        "current_year": getServerTime().year
    }
    return templates.TemplateResponse("tasks.html", context)


@router.get("/tasks/add", response_class=HTMLResponse)
async def add_task_page(
        request: Request,
        current_user: schemes.UserResponse = Depends(get_current_user),
        templates = Depends(get_templates)
):
    context = {
        "request": request,
        "user": current_user,
        "current_year": getServerTime().year
    }
    return templates.TemplateResponse( "taskAdd.html", context )

@router.get("/subjects", response_class=HTMLResponse)
async def subjects_page(
        request: Request,
        db: Session = Depends(get_db),
        current_user: schemes.UserResponse = Depends(get_current_user),
        templates = Depends(get_templates)
):
    """
    Страница управления предметами
    """

    user_subjects = crud_subjects.get_user_subjects(db, current_user.id)

    context = {
        "request": request,
        "user": current_user,
        "subjects": user_subjects,
        "current_year": getServerTime().year
    }
    return templates.TemplateResponse("subjects.html", context)


@router.get("/profile", response_class=HTMLResponse)
async def profile_page(
        request: Request,
        current_user: schemes.UserResponse = Depends(get_current_user),
        templates = Depends(get_templates)
):
    """
    Страница профиля пользователя
    """

    context = {
        "request": request,
        "user": current_user,
        "current_year": getServerTime().year
    }
    return templates.TemplateResponse("profile.html", context)


@router.get("/task/{task_id}", response_class=HTMLResponse)
async def task_detail_page(
        task_id: int,
        request: Request,
        db: Session = Depends(get_db),
        current_user: schemes.UserResponse = Depends(get_current_user),
        templates = Depends(get_templates)
):
    """
    Страница детальной информации о задаче
    """

    task = crud_tasks.get_task_by_id(db, task_id, current_user.id)
    if not task:
        # Редирект на 404 или список задач
        return RedirectResponse("/tasks")

    context = {
        "request": request,
        "user": current_user,
        "task": task,
        "current_year": getServerTime().year
    }
    return templates.TemplateResponse("task_detail.html", context)


# @router.get("/settings", response_class=HTMLResponse)
# async def settings_page(
#         request: Request,
#         current_user: schemes.UserResponse = Depends(get_current_user)
# ):
#     """
#     Страница настроек
#     """
#
#     context = {
#         "request": request,
#         "user": current_user,
#         "current_year": getServerTime().year
#     }
#     return templates.TemplateResponse("settings.html", context)


@router.get("/help", response_class=HTMLResponse)
async def help_page(request: Request , templates = Depends(get_templates)):
    """
    Страница помощи/FAQ
    """

    context = {
        "request": request,
        "current_year": getServerTime().year
    }
    return templates.TemplateResponse("help.html", context)


@router.get("/about", response_class=HTMLResponse)
async def about_page(request: Request, templates = Depends(get_templates)):
    """
    Страница "О проекте"
    """

    context = {
        "request": request,
        "current_year": getServerTime().year
    }
    return templates.TemplateResponse("about.html", context)

@router.get("/help", response_class=HTMLResponse)
async def about_page(request: Request, templates = Depends(get_templates)):
    """
    Страница "О проекте"
    """

    context = {
        "request": request,
        "current_year": getServerTime().year
    }
    return templates.TemplateResponse("about.html", context)


@router.get("/forgot-password", response_class=HTMLResponse)
async def forgot_password_page(request: Request, templates = Depends(get_templates)):
    # Страница забыл пароль
    context = {
        "request": request,
        "current_year": getServerTime().year
    }
    return templates.TemplateResponse("forgotPassword.html", context)


# Тест внутренней ошибки сервера
# @router.get("/err", response_class=HTMLResponse)
# async def testerr(request: Request, templates = Depends(get_templates)):
#     return False