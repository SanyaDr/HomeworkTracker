# backend/tests/test_database.py
import pytest
from sqlalchemy.orm import Session

# ОШИБКА: Функции debug_get_db_info нет - создадим простой тест
from app.models import User  # ← ИМПОРТИРУЙ МОДЕЛИ!

class TestDatabase:
    # Тест простого создания пользователя
    def test_simple_create_user(self, test_db: Session):
        user = User(
            email="test@example.com",
            login="testuser",
            name="Test User"
        )
        test_db.add(user)
        test_db.commit()

        # Проверяем что пользователь создан
        assert user.id is not None
        assert user.email == "test@example.com"

    def test_tables_exist(self, test_db: Session):
        """Тест что таблицы созданы"""
        # Простой запрос чтобы проверить что таблицы работают
        users = test_db.query(User).all()
        assert isinstance(users, list)  # Должен вернуть список (пустой)