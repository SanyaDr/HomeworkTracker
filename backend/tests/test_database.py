from sqlalchemy.exc import IntegrityError  # ← ЗАМЕНИТЕ ЭТУ СТРОКУ (было: from sqlite3 import IntegrityError)

import pytest
from sqlalchemy.orm import Session

from app.models import User, Subject, Task  # ← ИМПОРТИРУЙ МОДЕЛИ!
from app.enums import TaskStatus, TaskPriority

class TestDatabase:
    # Тест создания таблиц (пустых)
    def test_tables_exist(self, test_db: Session):
        users = test_db.query(User).all()
        assert isinstance(users, list)  # Должен вернуть список (пустой)

    # Тест простого создания пользователя
    def test_simple_create_user(self, test_db: Session):
        testdata={
            "email" : "test@example.com",
            "login" : "testuser",
            "name" : "Test User",
            "password" : "12345678"
        }

        user = User(
            email="test@example.com",
            login="testuser",
            name="Test User",
            hashed_password="12345678"

        )
        test_db.add(user)
        test_db.commit()

        # Проверяем что пользователь создан
        assert user.id is not None
        assert user.email == testdata["email"]
        assert user.login == testdata["login"]

    def test_create_user(self, test_db: Session):
        TestData={
            "login" : "MyTestUser",
            "email" : "mr.drovosekov2006@yandex.ru",
            "name" : "SanyaDr",
            "groupName": "БПМ-25-1",
            "password" : "12345678"
        }
        testUser = User(
            login=TestData["login"],
            email=TestData["email"],
            name=TestData["name"],
            groupName=TestData["groupName"],
            hashed_password=TestData["password"]
        )
        test_db.add(testUser)
        test_db.commit()
        test_db.refresh(testUser)

        assert testUser.id is not None
        assert testUser.email == TestData["email"]
        assert testUser.login == TestData["login"]
        assert testUser.name == TestData["name"]
        assert testUser.groupName == TestData["groupName"]
        assert testUser.hashed_password == TestData["password"]
        assert testUser.created_at is not None

    def test_user_unique_data(self, test_db:Session):
        td1 = {
            "login" : "User1",
            "email": "mr.drovosekov2006@yandex.ru",
            "name" : "user",
            "password" : "1234"
        }
        tUser1 = User(
            login = td1["login"],
            email = td1["email"],
            name = td1["name"],
            hashed_password = td1["password"]
        )
        tUser2 = User(
            login = td1["login"],
            email = td1["email"],
            name = td1["name"],
            hashed_password = td1["password"]
        )
        test_db.add(tUser1)
        test_db.commit()
        test_db.refresh(tUser1)

        with pytest.raises(IntegrityError):
            test_db.add(tUser2)
            test_db.commit()
            test_db.refresh(tUser2)

    def test_create_subject(self, test_db: Session):
        td = {
            "login" : "user1",
            "password" : "1234",

            "Subject" : "Math"
        }
        tUser = User(
            login = td["login"],
            hashed_password=td["password"]
        )
        test_db.add(tUser)
        test_db.commit()
        test_db.refresh(tUser)
        tSubject = Subject(
            user_id=tUser.id,
            name = td["Subject"]
        )
        test_db.add(tSubject)
        test_db.commit()
        test_db.refresh(tSubject)

        assert tSubject.id is not None
        assert tSubject.name == td["Subject"]
        assert tSubject.user_id == tUser.id
        assert tSubject.user.login == td["login"]

    def test_create_tasks(self, test_db: Session):
        td = {
            "login" : "user",
            "password" : "12345",

            "Subject" : "Math",

            "title" : "Do math matherfucker",
            "description" : "This is really important information! Do it please!",
        }

        tUser = User(
            login = td["login"],
            hashed_password=td["password"]
        )
        test_db.add(tUser)
        test_db.commit()
        test_db.refresh(tUser)
        tSubject = Subject(
            user_id=tUser.id,
            name = td["Subject"]
        )
        test_db.add(tSubject)
        test_db.commit()
        test_db.refresh(tSubject)
        tTask = Task(
            user_id = tUser.id,
            subject_id = tSubject.id,
            title = td["title"],
            status = TaskStatus.ASSIGNED,
            priority = TaskPriority.LOW,
        )
        test_db.add(tTask)
        test_db.commit()
        test_db.refresh(tTask)

        # Проверка индекса на status
        found = test_db.query(Task).filter(Task.status == TaskStatus.ASSIGNED).first()
        assert found is not None
        # Проверка индекса на priority
        found = test_db.query(Task).filter(Task.priority == TaskPriority.LOW).first()
        assert found is not None
        # Проверка индекса на deadline
        found = test_db.query(Task).filter(Task.deadline.isnot(None)).first()
        assert found is not None


    def test_cascade_delete_user(self, test_db: Session):
        """Тест каскадного удаления: удаление User удаляет Subjects и Tasks"""
        user = User(email="user@example.com", login="user", name="User")
        test_db.add(user)
        test_db.commit()

        subject = Subject(user_id=user.id, name="Math")
        test_db.add(subject)
        test_db.commit()

        task = Task(user_id=user.id, subject_id=subject.id, title="Test")
        test_db.add(task)
        test_db.commit()

        # Удаляем user
        test_db.delete(user)
        test_db.commit()

        # Проверяем, что subjects и tasks удалены
        assert test_db.query(Subject).filter(Subject.id == subject.id).first() is None
        assert test_db.query(Task).filter(Task.id == task.id).first() is None

    def test_cascade_delete_subject(self, test_db: Session):
        """Тест каскадного удаления: удаление Subject удаляет Tasks"""
        user = User(email="user@example.com", login="user", name="User")
        test_db.add(user)
        test_db.commit()

        subject = Subject(user_id=user.id, name="Math")
        test_db.add(subject)
        test_db.commit()

        task = Task(user_id=user.id, subject_id=subject.id, title="Test")
        test_db.add(task)
        test_db.commit()

        # Удаляем subject
        test_db.delete(subject)
        test_db.commit()

        # Проверяем, что task удалён
        assert test_db.query(Task).filter(Task.id == task.id).first() is None
