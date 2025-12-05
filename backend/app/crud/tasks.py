from sqlalchemy.orm import Session
from sqlalchemy import or_
from typing import List, Optional
from datetime import datetime
from app import schemes
from app.model import enums, models


def create_task(db: Session, task: schemes.TaskCreate, user_id: int) -> models.Task:
    """
    Создание новой задачи
    """
    db_task = models.Task(
        **task.model_dump(),
        user_id=user_id,
        status=enums.TaskStatus.ASSIGNED
    )
    db.add(db_task)
    db.commit()
    db.refresh(db_task)
    return db_task


def get_task_by_id(db: Session, task_id: int, user_id: Optional[int] = None) -> Optional[models.Task]:
    """
    Получение задачи по ID
    Если передан user_id, проверяем принадлежность задачи пользователю
    """
    query = db.query(models.Task).filter(models.Task.id == task_id)
    if user_id:
        query = query.filter(models.Task.user_id == user_id)
    return query.first()


def get_tasks(
        db: Session,
        user_id: int,
        filters: schemes.TaskFilter,
        include_overdue: bool = True
) -> tuple[List[models.Task], int]:
    """
    Получение списка задач с фильтрацией и пагинацией

    Если include_overdue=True, автоматически помечает просроченные задачи
    """
    query = db.query(models.Task).filter(models.Task.user_id == user_id)

    # Применяем фильтры
    if filters.status:
        query = query.filter(models.Task.status == filters.status)
    if filters.priority:
        query = query.filter(models.Task.priority == filters.priority)
    if filters.subject_id:
        query = query.filter(models.Task.subject_id == filters.subject_id)
    if filters.search:
        search_term = f"%{filters.search}%"
        query = query.filter(
            or_(
                models.Task.title.ilike(search_term),
                models.Task.description.ilike(search_term)
            )
        )

    # Автоматическая пометка просроченных задач
    if include_overdue:
        now = datetime.utcnow()
        # Находим задачи, которые просрочены но ещё в статусе ASSIGNED
        overdue_tasks = query.filter(
            models.Task.status == enums.TaskStatus.ASSIGNED,
            models.Task.deadline.isnot(None),
            models.Task.deadline < now
        ).all()

        for task in overdue_tasks:
            # Здесь можно обновить статус или добавить поле "просрочено"
            # В зависимости от требований
            pass  # Пока оставляем как есть, можно добавить логику позже

    # Получаем общее количество
    total = query.count()

    # Сортировка по дедлайну (сначала ближайшие)
    query = query.order_by(
        models.Task.deadline.asc().nulls_last(),
        models.Task.created_at.desc()
    )

    # Пагинация
    tasks = query.offset(filters.skip).limit(filters.limit).all()

    return tasks, total


def update_task(
        db: Session,
        task_id: int,
        task_update: schemes.TaskUpdate,
        user_id: Optional[int] = None
) -> Optional[models.Task]:
    """
    Обновление задачи
    """
    db_task = get_task_by_id(db, task_id, user_id)
    if not db_task:
        return None

    update_data = task_update.model_dump(exclude_unset=True)

    for field, value in update_data.items():
        setattr(db_task, field, value)

    # Обновляем время изменения
    # db_task.updated_at = datetime.utcnow()  # Если добавите поле в модель

    db.commit()
    db.refresh(db_task)
    return db_task


def delete_task(db: Session, task_id: int, user_id: Optional[int] = None) -> bool:
    """
    Удаление задачи
    Возвращает True если удалено, False если задача не найдена
    """
    db_task = get_task_by_id(db, task_id, user_id)
    if not db_task:
        return False

    db.delete(db_task)
    db.commit()
    return True


def complete_task(db: Session, task_id: int, user_id: Optional[int] = None) -> Optional[models.Task]:
    """
    Отметить задачу как выполненную
    """
    db_task = get_task_by_id(db, task_id, user_id)
    if not db_task:
        return None

    db_task.status = enums.TaskStatus.COMPLETED
    # db_task.updated_at = datetime.utcnow()  # Если добавите поле в модель

    db.commit()
    db.refresh(db_task)
    return db_task


def get_user_tasks_count(db: Session, user_id: int) -> dict:
    """
    Получение статистики по задачам пользователя
    """
    total = db.query(models.Task).filter(models.Task.user_id == user_id).count()
    completed = db.query(models.Task).filter(
        models.Task.user_id == user_id,
        models.Task.status == enums.TaskStatus.COMPLETED
    ).count()
    assigned = db.query(models.Task).filter(
        models.Task.user_id == user_id,
        models.Task.status == enums.TaskStatus.ASSIGNED
    ).count()

    # Задачи с дедлайном (опционально)
    with_deadline = db.query(models.Task).filter(
        models.Task.user_id == user_id,
        models.Task.deadline.isnot(None)
    ).count()

    return {
        "total": total,
        "completed": completed,
        "assigned": assigned,
        "with_deadline": with_deadline,
        "completion_rate": completed / total if total > 0 else 0
    }