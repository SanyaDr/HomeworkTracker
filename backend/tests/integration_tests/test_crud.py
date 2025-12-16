"""
Тесты CRUD операций через FastAPI эндпоинты
"""
import pytest
from fastapi.testclient import TestClient

class TestCRUD:
    """Тесты основных CRUD операций"""

    # ==================== USER CRUD TESTS ====================

    def test_create_user(self, client: TestClient):
        """Создание пользователя через API"""
        response = client.post("/api/users/", json={
            "email": "crud_test@example.com",
            "login": "cruduser",
            "name": "CRUD Test User",
            "password": "securepassword123"
        })

        assert response.status_code == 200
        data = response.json()

        assert data["email"] == "crud_test@example.com"
        assert data["login"] == "cruduser"
        assert data["name"] == "CRUD Test User"
        assert "id" in data
        assert "password" not in data  # пароль не должен возвращаться
        assert data["is_active"] is True  # значение по умолчанию

    def test_create_user_invalid_email(self, client: TestClient):
        """Попытка создать пользователя с невалидным email"""
        response = client.post("/api/users/", json={
            "email": "invalid-email",
            "login": "test",
            "name": "Test",
            "password": "123"
        })

        assert response.status_code == 422  # Validation error
        assert "email" in response.text.lower()

    def test_create_user_short_password(self, client: TestClient):
        """Попытка создать пользователя с коротким паролем"""
        response = client.post("/api/users/", json={
            "email": "valid@example.com",
            "login": "testuser",
            "name": "Test User",
            "password": "123"  # слишком короткий
        })

        assert response.status_code == 422

    def test_create_user_duplicate_email(self, client: TestClient, test_db):
        """Попытка создать пользователя с уже существующим email"""
        # Первый пользователь
        client.post("/api/users/", json={
            "email": "duplicate@example.com",
            "login": "user1",
            "name": "User One",
            "password": "password123"
        })

        # Второй пользователь с тем же email
        response = client.post("/api/users/", json={
            "email": "duplicate@example.com",  # тот же email!
            "login": "user2",
            "name": "User Two",
            "password": "password456"
        })

        # Должна быть ошибка (409 Conflict или 400)
        assert response.status_code in [400, 409, 422]

    def test_get_user_by_id(self, client: TestClient):
        """Получение пользователя по ID"""
        # Создаем пользователя
        create_resp = client.post("/api/users/", json={
            "email": "getbyid@example.com",
            "login": "getbyiduser",
            "name": "Get By ID User",
            "password": "password123"
        })
        user_id = create_resp.json()["id"]

        # Получаем пользователя
        get_resp = client.get(f"/api/users/{user_id}")
        assert get_resp.status_code == 200

        data = get_resp.json()
        assert data["id"] == user_id
        assert data["login"] == "getbyiduser"
        assert data["email"] == "getbyid@example.com"

    def test_get_nonexistent_user(self, client: TestClient):
        """Попытка получить несуществующего пользователя"""
        response = client.get("/api/users/999999")
        assert response.status_code == 404

    def test_update_user(self, client: TestClient):
        """Обновление данных пользователя"""
        # Создаем
        create_resp = client.post("/api/users/", json={
            "email": "update@example.com",
            "login": "updateuser",
            "name": "Old Name",
            "password": "password123"
        })
        user_id = create_resp.json()["id"]

        # Обновляем
        update_resp = client.put(f"/api/users/{user_id}", json={
            "name": "New Updated Name",
            "groupName": "10A"
        })
        assert update_resp.status_code == 200

        data = update_resp.json()
        assert data["name"] == "New Updated Name"
        assert data["groupName"] == "10A"

        # Проверяем что остальные поля не изменились
        assert data["email"] == "update@example.com"
        assert data["login"] == "updateuser"

    def test_partial_update_user(self, client: TestClient):
        """Частичное обновление пользователя"""
        create_resp = client.post("/api/users/", json={
            "email": "patch@example.com",
            "login": "patchuser",
            "name": "Patch User",
            "password": "password123"
        })
        user_id = create_resp.json()["id"]

        # Обновляем только имя
        patch_resp = client.patch(f"/api/users/{user_id}", json={
            "name": "Patched Name"
        })
        assert patch_resp.status_code == 200
        assert patch_resp.json()["name"] == "Patched Name"

    def test_delete_user(self, client: TestClient):
        """Удаление пользователя"""
        create_resp = client.post("/api/users/", json={
            "email": "delete@example.com",
            "login": "deleteuser",
            "name": "Delete Me",
            "password": "password123"
        })
        user_id = create_resp.json()["id"]

        # Удаляем
        delete_resp = client.delete(f"/api/users/{user_id}")
        assert delete_resp.status_code == 200

        # Проверяем что удалился
        get_resp = client.get(f"/api/users/{user_id}")
        assert get_resp.status_code == 404

    def test_list_users(self, client: TestClient):
        """Получение списка пользователей"""
        # Создаем несколько пользователей
        for i in range(3):
            client.post("/api/users/", json={
                "email": f"listuser{i}@example.com",
                "login": f"listuser{i}",
                "name": f"List User {i}",
                "password": f"password{i}"
            })

        # Получаем список
        response = client.get("/api/users/")
        assert response.status_code == 200

        users = response.json()
        assert isinstance(users, list)
        assert len(users) >= 3

    # ==================== SUBJECT CRUD TESTS ====================

    def test_create_subject(self, client: TestClient):
        """Создание предмета"""
        # Сначала создаем пользователя
        user_resp = client.post("/api/users/", json={
            "email": "subject_user@example.com",
            "login": "subjectuser",
            "name": "Subject User",
            "password": "password123"
        })
        user_id = user_resp.json()["id"]

        # Создаем предмет
        subject_resp = client.post("/api/subjects/", json={
            "name": "Mathematics",
            "color": "#FF5733",
            "user_id": user_id
        })

        assert subject_resp.status_code == 200
        data = subject_resp.json()

        assert data["name"] == "Mathematics"
        assert data["color"] == "#FF5733"
        assert data["user_id"] == user_id

    def test_create_subject_invalid_color(self, client: TestClient):
        """Попытка создать предмет с невалидным цветом"""
        user_resp = client.post("/api/users/", json={
            "email": "color_user@example.com",
            "login": "coloruser",
            "name": "Color User",
            "password": "password123"
        })
        user_id = user_resp.json()["id"]

        response = client.post("/api/subjects/", json={
            "name": "Invalid Color Subject",
            "color": "not-a-color",  # невалидный цвет
            "user_id": user_id
        })

        assert response.status_code == 422

    def test_get_subject_with_tasks(self, client: TestClient):
        """Получение предмета с заданиями"""
        # Создаем пользователя
        user_resp = client.post("/api/users/", json={
            "email": "subject_tasks@example.com",
            "login": "subjecttasks",
            "name": "Subject Tasks User",
            "password": "password123"
        })
        user_id = user_resp.json()["id"]

        # Создаем предмет
        subject_resp = client.post("/api/subjects/", json={
            "name": "Physics",
            "color": "#33FF57",
            "user_id": user_id
        })
        subject_id = subject_resp.json()["id"]

        # Создаем несколько заданий для предмета
        for i in range(2):
            client.post("/api/tasks/", json={
                "title": f"Physics Task {i}",
                "subject_id": subject_id,
                "user_id": user_id
            })

        # Получаем предмет с заданиями
        response = client.get(f"/api/subjects/{subject_id}?include_tasks=true")
        assert response.status_code == 200

        data = response.json()
        assert data["name"] == "Physics"
        assert "tasks" in data
        assert len(data["tasks"]) == 2

    # ==================== TASK CRUD TESTS ====================

    def test_create_task(self, client: TestClient):
        """Создание задания"""
        # Создаем пользователя
        user_resp = client.post("/api/users/", json={
            "email": "task_user@example.com",
            "login": "taskuser",
            "name": "Task User",
            "password": "password123"
        })
        user_id = user_resp.json()["id"]

        # Создаем предмет
        subject_resp = client.post("/api/subjects/", json={
            "name": "History",
            "color": "#3357FF",
            "user_id": user_id
        })
        subject_id = subject_resp.json()["id"]

        # Создаем задание
        task_resp = client.post("/api/tasks/", json={
            "title": "History Homework",
            "description": "Read chapter 5",
            "subject_id": subject_id,
            "priority": "high",
            "deadline": "2024-12-31T23:59:00"
        })

        assert task_resp.status_code == 200
        data = task_resp.json()

        assert data["title"] == "History Homework"
        assert data["description"] == "Read chapter 5"
        assert data["subject_id"] == subject_id
        assert data["priority"] == "high"
        assert data["status"] == "assigned"  # значение по умолчанию

    def test_create_task_without_deadline(self, client: TestClient):
        """Создание задания без дедлайна"""
        user_resp = client.post("/api/users/", json={
            "email": "nodeadline@example.com",
            "login": "nodeadline",
            "name": "No Deadline User",
            "password": "password123"
        })
        user_id = user_resp.json()["id"]

        subject_resp = client.post("/api/subjects/", json={
            "name": "Biology",
            "user_id": user_id
        })
        subject_id = subject_resp.json()["id"]

        task_resp = client.post("/api/tasks/", json={
            "title": "Biology Report",
            "subject_id": subject_id
        })

        assert task_resp.status_code == 200
        data = task_resp.json()

        assert data["deadline"] is None
        assert data["priority"] == "medium"  # значение по умолчанию

    def test_complete_task(self, client: TestClient):
        """Отметка задания как выполненного"""
        # Создаем цепочку: пользователь → предмет → задание
        user_resp = client.post("/api/users/", json={
            "email": "complete@example.com",
            "login": "completeuser",
            "name": "Complete User",
            "password": "password123"
        })
        user_id = user_resp.json()["id"]

        subject_resp = client.post("/api/subjects/", json={
            "name": "Chemistry",
            "user_id": user_id
        })
        subject_id = subject_resp.json()["id"]

        task_resp = client.post("/api/tasks/", json={
            "title": "Chemistry Experiment",
            "subject_id": subject_id
        })
        task_id = task_resp.json()["id"]

        # Отмечаем как выполненное
        complete_resp = client.patch(f"/api/tasks/{task_id}/complete")
        assert complete_resp.status_code == 200

        data = complete_resp.json()
        assert data["status"] == "completed"

        # Проверяем через GET
        get_resp = client.get(f"/api/tasks/{task_id}")
        assert get_resp.json()["status"] == "completed"

    def test_filter_tasks_by_status(self, client: TestClient):
        """Фильтрация заданий по статусу"""
        user_resp = client.post("/api/users/", json={
            "email": "filter@example.com",
            "login": "filteruser",
            "name": "Filter User",
            "password": "password123"
        })
        user_id = user_resp.json()["id"]

        subject_resp = client.post("/api/subjects/", json={
            "name": "Filter Subject",
            "user_id": user_id
        })
        subject_id = subject_resp.json()["id"]

        # Создаем задания с разными статусами
        task1 = client.post("/api/tasks/", json={
            "title": "Task 1 - Assigned",
            "subject_id": subject_id,
            "status": "assigned"
        })

        task2 = client.post("/api/tasks/", json={
            "title": "Task 2 - Completed",
            "subject_id": subject_id,
            "status": "completed"
        })

        # Фильтруем по статусу "assigned"
        filter_resp = client.get(f"/api/tasks/?status=assigned&subject_id={subject_id}")
        assert filter_resp.status_code == 200

        tasks = filter_resp.json()
        assert isinstance(tasks, list)
        # Должен быть только один assigned
        assigned_tasks = [t for t in tasks if t["status"] == "assigned"]
        assert len(assigned_tasks) >= 1

    def test_search_tasks(self, client: TestClient):
        """Поиск заданий по названию"""
        user_resp = client.post("/api/users/", json={
            "email": "search@example.com",
            "login": "searchuser",
            "name": "Search User",
            "password": "password123"
        })
        user_id = user_resp.json()["id"]

        subject_resp = client.post("/api/subjects/", json={
            "name": "Search Subject",
            "user_id": user_id
        })
        subject_id = subject_resp.json()["id"]

        # Создаем задания с разными названиями
        client.post("/api/tasks/", json={
            "title": "Математика: решить уравнения",
            "subject_id": subject_id
        })

        client.post("/api/tasks/", json={
            "title": "Физика: лабораторная работа",
            "subject_id": subject_id
        })

        client.post("/api/tasks/", json={
            "title": "История: доклад о войне",
            "subject_id": subject_id
        })

        # Ищем "математика"
        search_resp = client.get(f"/api/tasks/?search=математика&subject_id={subject_id}")
        assert search_resp.status_code == 200

        tasks = search_resp.json()
        # Должно найти хотя бы одно задание с "математика"
        assert any("математика" in t["title"].lower() for t in tasks)

    def test_pagination(self, client: TestClient):
        """Пагинация при получении заданий"""
        user_resp = client.post("/api/users/", json={
            "email": "pagination@example.com",
            "login": "paginationuser",
            "name": "Pagination User",
            "password": "password123"
        })
        user_id = user_resp.json()["id"]

        subject_resp = client.post("/api/subjects/", json={
            "name": "Pagination Subject",
            "user_id": user_id
        })
        subject_id = subject_resp.json()["id"]

        # Создаем 15 заданий
        for i in range(15):
            client.post("/api/tasks/", json={
                "title": f"Task {i}",
                "subject_id": subject_id
            })

        # Получаем первую страницу (10 заданий по умолчанию)
        page1_resp = client.get(f"/api/tasks/?subject_id={subject_id}&skip=0&limit=10")
        page1_tasks = page1_resp.json()
        assert len(page1_tasks) == 10

        # Получаем вторую страницу
        page2_resp = client.get(f"/api/tasks/?subject_id={subject_id}&skip=10&limit=10")
        page2_tasks = page2_resp.json()
        assert len(page2_tasks) == 5  # осталось только 5

        # Проверяем что задания разные
        page1_ids = {t["id"] for t in page1_tasks}
        page2_ids = {t["id"] for t in page2_tasks}
        assert page1_ids.isdisjoint(page2_ids)  # не должно быть пересечений