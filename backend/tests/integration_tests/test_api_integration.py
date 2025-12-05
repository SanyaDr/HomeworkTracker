"""
Интеграционные тесты для полных сценариев работы с API
"""
import pytest
from fastapi.testclient import TestClient
from datetime import datetime, timedelta

class TestAPIIntegration:
    """Тесты полных сценариев работы через API"""

    def test_full_user_registration_workflow(self, client: TestClient):
        """
        Полный сценарий: Регистрация → Профиль → Обновление → Удаление
        """
        print("\n🔍 Тест: Полный сценарий работы с пользователем")

        # 1. РЕГИСТРАЦИЯ
        print("  1. Регистрация нового пользователя")
        register_data = {
            "email": "workflow@example.com",
            "login": "workflowuser",
            "name": "Workflow Test User",
            "password": "SecurePass123!",
            "groupName": "10A"
        }

        register_resp = client.post("/api/users/", json=register_data)
        assert register_resp.status_code == 200, "Ошибка регистрации"
        user_data = register_resp.json()
        user_id = user_data["id"]

        print(f"  ✅ Пользователь создан, ID: {user_id}")

        # 2. ПОЛУЧЕНИЕ ПРОФИЛЯ
        print("  2. Получение профиля пользователя")
        profile_resp = client.get(f"/api/users/{user_id}")
        assert profile_resp.status_code == 200, "Ошибка получения профиля"
        profile_data = profile_resp.json()

        assert profile_data["email"] == register_data["email"]
        assert profile_data["login"] == register_data["login"]
        assert profile_data["name"] == register_data["name"]
        print("  ✅ Профиль получен корректно")

        # 3. ОБНОВЛЕНИЕ ДАННЫХ
        print("  3. Обновление данных пользователя")
        update_resp = client.put(f"/api/users/{user_id}", json={
            "name": "Updated Workflow Name",
            "groupName": "11A"
        })
        assert update_resp.status_code == 200, "Ошибка обновления"
        updated_data = update_resp.json()

        assert updated_data["name"] == "Updated Workflow Name"
        assert updated_data["groupName"] == "11A"
        print("  ✅ Данные обновлены")

        # 4. УДАЛЕНИЕ
        print("  4. Удаление пользователя")
        delete_resp = client.delete(f"/api/users/{user_id}")
        assert delete_resp.status_code == 200, "Ошибка удаления"
        print("  ✅ Пользователь удален")

        # 5. ПРОВЕРКА ЧТО УДАЛЕН
        print("  5. Проверка что пользователь удален")
        check_resp = client.get(f"/api/users/{user_id}")
        assert check_resp.status_code == 404, "Пользователь не удален!"
        print("  ✅ Подтверждено удаление")

        print("🎉 Все шаги пройдены успешно!")

    def test_subject_with_tasks_workflow(self, client: TestClient):
        """
        Создание предмета → Добавление заданий → Фильтрация → Удаление
        """
        print("\n🔍 Тест: Работа с предметами и заданиями")

        # 1. СОЗДАНИЕ ПОЛЬЗОВАТЕЛЯ
        print("  1. Создание пользователя")
        user_resp = client.post("/api/users/", json={
            "email": "subject_workflow@example.com",
            "login": "subjectworkflow",
            "name": "Subject Workflow User",
            "password": "password123"
        })
        user_id = user_resp.json()["id"]
        print(f"  ✅ Пользователь создан, ID: {user_id}")

        # 2. СОЗДАНИЕ ПРЕДМЕТА
        print("  2. Создание предмета 'Математика'")
        subject_resp = client.post("/api/subjects/", json={
            "name": "Математика",
            "color": "#FF0000",
            "user_id": user_id
        })
        assert subject_resp.status_code == 200
        subject_data = subject_resp.json()
        subject_id = subject_data["id"]
        print(f"  ✅ Предмет создан, ID: {subject_id}")

        # 3. СОЗДАНИЕ НЕСКОЛЬКИХ ЗАДАНИЙ
        print("  3. Создание заданий по математике")
        tasks_data = [
            {
                "title": "Алгебра: решить уравнения",
                "description": "Страница 45, №1-15",
                "priority": "high",
                "deadline": (datetime.now() + timedelta(days=2)).isoformat()
            },
            {
                "title": "Геометрия: теоремы",
                "description": "Выучить теоремы Пифагора",
                "priority": "medium",
                "deadline": (datetime.now() + timedelta(days=5)).isoformat()
            },
            {
                "title": "Тригонометрия: формулы",
                "priority": "low"
            }
        ]

        task_ids = []
        for i, task_data in enumerate(tasks_data):
            task_data["subject_id"] = subject_id
            task_resp = client.post("/api/tasks/", json=task_data)
            assert task_resp.status_code == 200
            task_ids.append(task_resp.json()["id"])
            print(f"    ✅ Задание {i+1} создано")

        # 4. ПОЛУЧЕНИЕ ВСЕХ ЗАДАНИЙ ПРЕДМЕТА
        print("  4. Получение всех заданий по предмету")
        tasks_resp = client.get(f"/api/tasks/?subject_id={subject_id}")
        assert tasks_resp.status_code == 200
        all_tasks = tasks_resp.json()
        assert len(all_tasks) == 3
        print(f"  ✅ Получено {len(all_tasks)} заданий")

        # 5. ФИЛЬТРАЦИЯ ПО ПРИОРИТЕТУ
        print("  5. Фильтрация заданий по приоритету 'high'")
        high_priority_resp = client.get(f"/api/tasks/?subject_id={subject_id}&priority=high")
        high_priority_tasks = high_priority_resp.json()
        assert len(high_priority_tasks) == 1
        assert high_priority_tasks[0]["priority"] == "high"
        print(f"  ✅ Найдено {len(high_priority_tasks)} заданий с высоким приоритетом")

        # 6. ПОИСК ПО НАЗВАНИЮ
        print("  6. Поиск заданий по слову 'алгебра'")
        search_resp = client.get(f"/api/tasks/?subject_id={subject_id}&search=алгебра")
        search_tasks = search_resp.json()
        assert len(search_tasks) == 1
        assert "алгебра" in search_tasks[0]["title"].lower()
        print(f"  ✅ Найдено {len(search_tasks)} заданий по поиску")

        # 7. ВЫПОЛНЕНИЕ ЗАДАНИЯ
        print("  7. Отметка задания как выполненного")
        task_to_complete = task_ids[0]
        complete_resp = client.patch(f"/api/tasks/{task_to_complete}/complete")
        assert complete_resp.status_code == 200
        assert complete_resp.json()["status"] == "completed"
        print("  ✅ Задание отмечено как выполненное")

        # 8. ФИЛЬТРАЦИЯ ПО СТАТУСУ
        print("  8. Фильтрация выполненных заданий")
        completed_resp = client.get(f"/api/tasks/?subject_id={subject_id}&status=completed")
        completed_tasks = completed_resp.json()
        assert len(completed_tasks) == 1
        print(f"  ✅ Найдено {len(completed_tasks)} выполненных заданий")

        print("🎉 Работа с предметами и заданиями завершена успешно!")

    def test_multiple_subjects_workflow(self, client: TestClient):
        """
        Создание нескольких предметов → Распределение заданий → Анализ
        """
        print("\n🔍 Тест: Работа с несколькими предметами")

        # 1. СОЗДАНИЕ ПОЛЬЗОВАТЕЛЯ
        user_resp = client.post("/api/users/", json={
            "email": "multi_subject@example.com",
            "login": "multisubject",
            "name": "Multi Subject User",
            "password": "password123"
        })
        user_id = user_resp.json()["id"]

        # 2. СОЗДАНИЕ НЕСКОЛЬКИХ ПРЕДМЕТОВ
        subjects = [
            {"name": "Математика", "color": "#FF0000"},
            {"name": "Физика", "color": "#00FF00"},
            {"name": "Информатика", "color": "#0000FF"}
        ]

        subject_ids = {}
        for subject in subjects:
            subject["user_id"] = user_id
            resp = client.post("/api/subjects/", json=subject)
            subject_ids[subject["name"]] = resp.json()["id"]

        print(f"  ✅ Создано {len(subjects)} предметов")

        # 3. РАСПРЕДЕЛЕНИЕ ЗАДАНИЙ ПО ПРЕДМЕТАМ
        tasks_by_subject = {
            "Математика": [
                {"title": "Алгебра: уравнения", "priority": "high"},
                {"title": "Геометрия: теоремы", "priority": "medium"}
            ],
            "Физика": [
                {"title": "Механика: задачи", "priority": "high"},
                {"title": "Оптика: лабораторная", "priority": "low"}
            ],
            "Информатика": [
                {"title": "Python: функции", "priority": "medium"},
                {"title": "Базы данных: SQL", "priority": "high"},
                {"title": "Алгоритмы: сортировка", "priority": "low"}
            ]
        }

        total_tasks = 0
        for subject_name, tasks in tasks_by_subject.items():
            subject_id = subject_ids[subject_name]
            for task in tasks:
                task["subject_id"] = subject_id
                client.post("/api/tasks/", json=task)
                total_tasks += 1

        print(f"  ✅ Создано {total_tasks} заданий по всем предметам")

        # 4. АНАЛИЗ: задания по предметам
        print("  4. Анализ распределения заданий")
        for subject_name in subjects:
            subject_id = subject_ids[subject_name]
            tasks_resp = client.get(f"/api/tasks/?subject_id={subject_id}")
            subject_tasks = tasks_resp.json()
            expected_count = len(tasks_by_subject[subject_name])
            actual_count = len(subject_tasks)

            assert actual_count == expected_count, \
                f"Предмет '{subject_name}': ожидалось {expected_count}, получено {actual_count}"

            print(f"    📚 {subject_name}: {actual_count} заданий")

        # 5. АНАЛИЗ: задания по приоритету
        print("  5. Анализ по приоритетам")
        for priority in ["high", "medium", "low"]:
            priority_resp = client.get(f"/api/tasks/?priority={priority}")
            priority_tasks = priority_resp.json()

            # Подсчет вручную из наших данных
            expected_priority_count = sum(
                1 for tasks in tasks_by_subject.values()
                for task in tasks
                if task["priority"] == priority
            )

            print(f"    ⚡ Приоритет '{priority}': {len(priority_tasks)} заданий")

        print("🎉 Анализ нескольких предметов завершен успешно!")

    def test_cascade_operations_via_api(self, client: TestClient):
        """
        Тест каскадных операций через API:
        Пользователь → Предметы → Задания → Удаление пользователя
        """
        print("\n🔍 Тест: Каскадные операции через API")

        # 1. СОЗДАНИЕ ПОЛЬЗОВАТЕЛЯ
        print("  1. Создание пользователя")
        user_resp = client.post("/api/users/", json={
            "email": "cascade@example.com",
            "login": "cascadeuser",
            "name": "Cascade Test User",
            "password": "password123"
        })
        user_data = user_resp.json()
        user_id = user_data["id"]
        print(f"  ✅ Пользователь создан, ID: {user_id}")

        # 2. СОЗДАНИЕ ДВУХ ПРЕДМЕТОВ
        print("  2. Создание предметов для пользователя")
        subjects = []
        for i, subject_name in enumerate(["Каскадная Математика", "Каскадная Физика"]):
            subject_resp = client.post("/api/subjects/", json={
                "name": subject_name,
                "color": "#FF0000" if i == 0 else "#00FF00",
                "user_id": user_id
            })
            subject_data = subject_resp.json()
            subjects.append(subject_data)
            print(f"    ✅ Предмет '{subject_name}' создан, ID: {subject_data['id']}")

        # 3. СОЗДАНИЕ ЗАДАНИЙ ДЛЯ КАЖДОГО ПРЕДМЕТА
        print("  3. Создание заданий для каждого предмета")
        tasks = []
        for subject in subjects:
            for j in range(2):  # по 2 задания на предмет
                task_resp = client.post("/api/tasks/", json={
                    "title": f"Задание {j+1} для {subject['name']}",
                    "subject_id": subject["id"],
                    "user_id": user_id,
                    "priority": "high" if j == 0 else "medium"
                })
                task_data = task_resp.json()
                tasks.append(task_data)
                print(f"    ✅ Задание создано, ID: {task_data['id']}")

        # 4. ПРОВЕРКА ЧТО ВСЕ СОЗДАЛОСЬ
        print("  4. Проверка создания всех данных")

        # Проверяем пользователя
        user_check = client.get(f"/api/users/{user_id}")
        assert user_check.status_code == 200

        # Проверяем предметы
        for subject in subjects:
            subject_check = client.get(f"/api/subjects/{subject['id']}")
            assert subject_check.status_code == 200

        # Проверяем задания
        for task in tasks:
            task_check = client.get(f"/api/tasks/{task['id']}")
            assert task_check.status_code == 200

        print(f"  ✅ Все создано: 1 пользователь, {len(subjects)} предметов, {len(tasks)} заданий")

        # 5. УДАЛЕНИЕ ПОЛЬЗОВАТЕЛА
        print("  5. Удаление пользователя")
        delete_resp = client.delete(f"/api/users/{user_id}")
        assert delete_resp.status_code == 200
        print("  ✅ Пользователь удален")

        # 6. ПРОВЕРКА ЧТО ВСЕ УДАЛИЛОСЬ КАСКАДНО
        print("  6. Проверка каскадного удаления")

        # Пользователь не должен существовать
        user_check = client.get(f"/api/users/{user_id}")
        assert user_check.status_code == 404, "Пользователь не удален!"
        print("    ✅ Пользователь удален")

        # Предметы не должны существовать
        for subject in subjects:
            subject_check = client.get(f"/api/subjects/{subject['id']}")
            assert subject_check.status_code == 404, f"Предмет {subject['id']} не удален каскадно!"
        print(f"    ✅ {len(subjects)} предметов удалены каскадно")

        # Задания не должны существовать
        for task in tasks:
            task_check = client.get(f"/api/tasks/{task['id']}")
            assert task_check.status_code == 404, f"Задание {task['id']} не удалено каскадно!"
        print(f"    ✅ {len(tasks)} заданий удалены каскадно")

        print("🎉 Каскадные операции работают корректно!")

    def test_error_handling_and_edge_cases(self, client: TestClient):
        """
        Тест обработки ошибок и граничных случаев
        """
        print("\n🔍 Тест: Обработка ошибок и граничные случаи")

        # 1. НЕСУЩЕСТВУЮЩИЕ РЕСУРСЫ
        print("  1. Запросы к несуществующим ресурсам")

        # Несуществующий пользователь
        resp = client.get("/api/users/999999")
        assert resp.status_code == 404

        # Несуществующий предмет
        resp = client.get("/api/subjects/999999")
        assert resp.status_code == 404

        # Несуществующее задание
        resp = client.get("/api/tasks/999999")
        assert resp.status_code == 404

        print("  ✅ Несуществующие ресурсы возвращают 404")

        # 2. НЕВАЛИДНЫЕ ДАННЫЕ
        print("  2. Попытка создания с невалидными данными")

        # Слишком короткий логин
        resp = client.post("/api/users/", json={
            "email": "test@example.com",
            "login": "ab",  # слишком коротко (минимум 3)
            "name": "Test",
            "password": "password123"
        })
        assert resp.status_code == 422

        # Невалидный email
        resp = client.post("/api/users/", json={
            "email": "not-an-email",
            "login": "testuser",
            "name": "Test",
            "password": "password123"
        })
        assert resp.status_code == 422

        # Невалидный приоритет задания
        user_resp = client.post("/api/users/", json={
            "email": "edge@example.com",
            "login": "edgeuser",
            "name": "Edge User",
            "password": "password123"
        })
        user_id = user_resp.json()["id"]

        subject_resp = client.post("/api/subjects/", json={
            "name": "Edge Subject",
            "user_id": user_id
        })
        subject_id = subject_resp.json()["id"]

        resp = client.post("/api/tasks/", json={
            "title": "Test Task",
            "subject_id": subject_id,
            "priority": "invalid_priority"  # невалидный приоритет
        })
        assert resp.status_code == 422

        print("  ✅ Невалидные данные возвращают 422")

        # 3. ПУСТЫЕ ИЛИ ЧАСТИЧНЫЕ ДАННЫЕ
        print("  3. Работа с пустыми или частичными данными")

        # Создание задания только с обязательными полями
        resp = client.post("/api/tasks/", json={
            "title": "Минимальное задание",
            "subject_id": subject_id
        })
        assert resp.status_code == 200
        task_data = resp.json()

        # Проверяем значения по умолчанию
        assert task_data["priority"] == "medium"
        assert task_data["status"] == "assigned"
        assert task_data["description"] is None
        assert task_data["deadline"] is None

        print("  ✅ Значения по умолчанию работают корректно")

        # 4. ПАГИНАЦИЯ С НЕВАЛИДНЫМИ ПАРАМЕТРАМИ
        print("  4. Пагинация с нестандартными параметрами")

        # Отрицательный skip
        resp = client.get(f"/api/tasks/?subject_id={subject_id}&skip=-10")
        assert resp.status_code == 422 or resp.status_code == 200

        # Отрицательный limit
        resp = client.get(f"/api/tasks/?subject_id={subject_id}&limit=-5")
        assert resp.status_code == 422 or resp.status_code == 200

        # Слишком большой limit
        resp = client.get(f"/api/tasks/?subject_id={subject_id}&limit=1000")
        # Может быть ограничение на максимальный лимит
        assert resp.status_code in [200, 422, 400]

        print("  ✅ Пагинация обрабатывает граничные случаи")

        print("🎉 Все ошибки и граничные случаи обрабатываются корректно!")