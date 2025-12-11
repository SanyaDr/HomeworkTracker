
import os
from dotenv import load_dotenv
load_dotenv()

app_path = "app.main:app"
# host = "127.0.0.1"
# port = 8080
# reload = True
# log_level = "info"

# Конфигурация сервера
host = os.getenv("HOST", "127.0.0.1")
port = int(os.getenv("PORT", 8000))
reload = os.getenv("RELOAD", "True").lower() == "true"
log_level = os.getenv("LOG_LEVEL", "info")

# JWT конфигурация
SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-key-change-in-production")
ALGORITHM = os.getenv("ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 30))

# def init_db():
#     """Инициализация базы данных"""
#     from .database import Base, engine
#     import asyncio
#
#     async def async_init():
#         async with engine.begin() as conn:
#             # Для async создаем таблицы
#             await conn.run_sync(Base.metadata.create_all)
#         print("✅ База данных инициализирована")
#
#     # Запускаем async инициализацию
#     asyncio.run(async_init())

# def create_admin_user():
#     """Создание администратора по умолчанию"""
#     from .database import AsyncSessionLocal
#     from app.crud import users as crud_users
#     from app.schemes import UserCreate
#     import asyncio
#
#     async def async_create_admin():
#         async with AsyncSessionLocal() as db:
#             # Проверяем существует ли администратор
#             admin = await db.execute(
#                 "SELECT * FROM users WHERE login = 'admin'"
#             )
#             if not admin.scalar():
#                 admin_user = UserCreate(
#                     login="admin",
#                     email="admin@example.com",
#                     name="Администратор",
#                     password="admin123",  # Измените в продакшене!
#                     groupName="Администрация"
#                 )
#                 await crud_users.create_user(db, admin_user)
#                 print("✅ Администратор создан")
#             else:
#                 print("ℹ️ Администратор уже существует")
#
#     asyncio.run(async_create_admin())