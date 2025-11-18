import os

from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import sessionmaker

# from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncAttrs
# from sqlalchemy.orm import DeclarativeBase, declared_attr

Base = declarative_base()
# Для SQLite
SQLALCHEMY_DATABASE_URL = "sqlite:///./database/homework_tracker.db"
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

def get_db():
    print("Создание локальной сессии")
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def create_tables():
    print("Создание таблиц в базе данных...")
    Base.metadata.create_all(bind=engine)
    print("Таблицы успешно созданы!")





# Функция для проверки подключения к БД
def debug_test_connection():
    try:
        with engine.connect() as conn:
            print("✅ Подключение к базе данных успешно!")
            return True
    except Exception as e:
        print(f"❌ Ошибка подключения к базе данных: {e}")
        return False

# Функция для получения информации о БД
def debug_get_db_info():
    return {
        "tables": list(Base.metadata.tables.keys()),
        "table_count": len(Base.metadata.tables)
    }