import os

from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import sessionmaker

from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncAttrs
from sqlalchemy.orm import DeclarativeBase, declared_attr

# from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
# from sqlalchemy.orm import sessionmaker, declarative_base
# import os
#
# # Async PostgreSQL URL (asyncpg драйвер)
# DATABASE_URL = os.getenv(
#     "DATABASE_URL",
#     "postgresql+asyncpg://homework_user:ваш_пароль@localhost:5432/homework_tracker"
# )
#
# # Для разработки можно использовать SQLite
# if os.getenv("ENVIRONMENT") == "development":
#     DATABASE_URL = "sqlite+aiosqlite:///./homework.db"
#     print("⚠️ Используется SQLite для разработки")
# else:
#     print(f"✅ Используется PostgreSQL: {DATABASE_URL.split('@')[-1]}")
#
# # Создаем async engine
# engine = create_async_engine(
#     DATABASE_URL,
#     echo=False,
#     future=True,
#     pool_size=20,
#     max_overflow=30,
#     pool_recycle=3600,
# )
#
# # Async сессия
# AsyncSessionLocal = sessionmaker(
#     engine,
#     class_=AsyncSession,
#     expire_on_commit=False
# )
#
# Base = declarative_base()
#
# # Dependency для получения async сессии
# async def get_db():
#     async with AsyncSessionLocal() as session:
#         try:
#             yield session
#             await session.commit()
#         except Exception:
#             await session.rollback()
#             raise
#         finally:
#             await session.close()

Base = declarative_base()
# Для SQLite
SQLALCHEMY_DATABASE_URL = "sqlite:///./database/homework_tracker.db"
current_dir = os.path.dirname(os.path.abspath(__file__))  # backend/app/core/
# print(f"📁 Текущая директория: {current_dir}")

# Для PostgreSQL (раскомментировать когда будет нужен)
# SQLALCHEMY_DATABASE_URL = "postgresql://username:password@localhost/homework_tracker"
# Движок
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    # Для SQLite нужно добавить этот параметр
    connect_args={"check_same_thread": False} if "sqlite" in SQLALCHEMY_DATABASE_URL else {}
)
# Фабрика сессий
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Определяем где должна быть база данных
# Вариант 1: В папке проекта (рекомендуется)
project_root = os.path.dirname(os.path.dirname(os.path.dirname(current_dir)))  # корень проекта
database_dir = os.path.join(project_root, "database")
os.makedirs(database_dir, exist_ok=True)
DATABASE_PATH = os.path.join(database_dir, "homework_tracker.db")

# print("Путь к БД ----------------->:", DATABASE_PATH)

def init_db():
    """Создает базу данных и все таблицы, если они не существуют"""
    try:
        # Проверяем существование файла базы данных
        # db_file = ".../database/homework_tracker.db"
        # db_exists = os.path.exists(DATABASE_PATH)

        # Создаем все таблицы
        Base.metadata.create_all(bind=engine)

        # if not db_exists:
        #     print("✅ База данных создана успешно!")
        # else:
        #     print("✅ База данных подключена!")

    except Exception as e:
        print(f"❌ Ошибка при создании базы данных: {e}")
        raise
    # Base.metadata.create_all(bind=engine)
    # print("База данных инициализирована")


def get_db():
    # print("Создание локальной сессии")
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def create_tables():
    # print("Создание таблиц в базе данных...")
    Base.metadata.create_all(bind=engine)
    # print("Таблицы успешно созданы!")


# Функция для проверки подключения к БД
def debug_test_connection():
    try:
        with engine.connect() as conn:
            print("Подключение к базе данных успешно!")
            return True
    except Exception as e:
        print(f"Ошибка подключения к базе данных: {e}")
        return False

# Функция для получения информации о БД
def debug_get_db_info():
    return {
        "tables": list(Base.metadata.tables.keys()),
        "table_count": len(Base.metadata.tables)
    }