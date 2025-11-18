import os
import tempfile
# import logging  # Для отладки

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.main import app
from app.database import Base, get_db

# ЯВНЫЙ ИМПОРТ ВСЕХ МОДЕЛЕЙ — ОБЯЗАТЕЛЬНО!
from app.models import User, Subject, Task

# Включаем логирование SQL для отладки (уберите после исправления)
# logging.basicConfig()
# logging.getLogger('sqlalchemy.engine').setLevel(logging.INFO)

@pytest.fixture(scope="function")
def test_db():
    # Создаём временный файл для базы данных
    db_file = tempfile.NamedTemporaryFile(delete=False, suffix='.db')
    db_file.close()
    TEST_DATABASE_URL = f"sqlite:///{db_file.name}"

    engine = create_engine(TEST_DATABASE_URL, connect_args={"check_same_thread": False})
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

    # Очищаем и создаём таблицы
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)

    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        engine.dispose()
        os.unlink(db_file.name)

@pytest.fixture(scope="function", autouse=True)
def create_test_dirs():
    os.makedirs("frontend/static", exist_ok=True)
    os.makedirs("frontend/templates", exist_ok=True)
    yield

@pytest.fixture(scope="function")
def client(test_db):
    def override_get_db():
        try:
            yield test_db
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    client = TestClient(app)
    yield client
    app.dependency_overrides.clear()