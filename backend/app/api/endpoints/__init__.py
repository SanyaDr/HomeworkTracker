"""
API endpoints (роутеры) приложения
"""

from .users import router as users_router
from .tasks import router as tasks_router
from .subjects import router as subjects_router
from .frontEndpoints import router as frontend_router

# Создаем список всех роутеров
api_routers = [
    users_router,
    tasks_router,
    subjects_router,
]

frontend_routers = [
    frontend_router
]

all_routers = api_routers + frontend_routers

__all__ = [
    "api_routers",
    "frontend_routers",
    "all_routers",
    "users_router",
    "tasks_router",
    "subjects_router",
    "frontend_router"
]