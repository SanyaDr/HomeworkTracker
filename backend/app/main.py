from fastapi import FastAPI

app = FastAPI(title="Homework Tracker", version="0.0.1")

# TODO async def ??

@app.get("/")
def read_root():
    return {"message": "Добро пожаловать в Трекер домашних заданий!"}

@app.get("/api/assignments/")
def get_assignments():
    # Пока это тестовые данные - потом заменим на реальные
    return [
        {"id": 1, "subject": "Математика", "title": "Проект по алгебре", "status": "active"},
        {"id": 2, "subject": "Информатика", "title": "Написать API", "status": "completed"}
    ]