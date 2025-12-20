"""
Core модули приложения (конфигурация, БД, аутентификация)
"""

from .database import Base, engine, SessionLocal, get_db
# from .auth import (
#     get_current_user,
#     create_access_token,
#     verify_token,
#     oauth2_scheme,
#     SECRET_KEY,
#     ALGORITHM,
#     ACCESS_TOKEN_EXPIRE_MINUTES
# )
from .database import init_db #, create_admin_user
from .templates import get_templates

__all__ = [
    "Base",
    "engine",
    "SessionLocal",
    "get_db",
    "init_db",
    "get_templates",
    # "create_admin_user",
]