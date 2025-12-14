from sqlalchemy.orm import Session
from sqlalchemy import or_
from typing import List, Optional
from datetime import datetime

# TODO Поправь временную зону datetime
def create_task(db: Session, task, user_id: int) :
    """
    Создание новой задачи
    """
    from ..model import Task, enums

    db_task = Task(
        **task.model_dump(),
        user_id=user_id,
        status=enums.TaskStatus.ASSIGNED
    )
    db.add(db_task)
    db.commit()
    db.refresh(db_task)
    return db_task


def get_task_by_id(db: Session, task_id: int, user_id: Optional[int] = None) -> Optional["Task"]:
    """
    Получение задачи по ID
    Если передан user_id, проверяем принадлежность задачи пользователю
    """
    from ..model import Task
    query = db.query(Task).filter(Task.id == task_id)
    if user_id:
        query = query.filter(Task.user_id == user_id)
    return query.first()


def get_tasks(
        db: Session,
        user_id: int,
        filters,
        include_overdue: bool = True
):
    """
    Получение списка задач с фильтрацией и пагинацией

    Если include_overdue=True, автоматически помечает просроченные задачи
    """
    from ..model import Task, enums  # ← относительный импорт

    query = db.query(Task).filter(Task.user_id == user_id)

    # Применяем фильтры
    if filters.status:
        query = query.filter(Task.status == filters.status)
    if filters.priority:
        query = query.filter(Task.priority == filters.priority)
    if filters.subject_id:
        query = query.filter(Task.subject_id == filters.subject_id)
    if filters.search:
        search_term = f"%{filters.search}%"
        query = query.filter(
            or_(
                Task.title.ilike(search_term),
                Task.description.ilike(search_term)
            )
        )

    # Автоматическая пометка просроченных задач
    if include_overdue:
        now = datetime.utcnow()
        # Находим задачи, которые просрочены но ещё в статусе ASSIGNED
        overdue_tasks = query.filter(
            Task.status == enums.TaskStatus.ASSIGNED,
            Task.deadline.isnot(None),
            Task.deadline < now
        ).all()

        for task in overdue_tasks:
            # TODO automatic overdue tasks
            # Здесь можно обновить статус или добавить поле "просрочено"
            # В зависимости от требований
            pass  # Пока оставляем как есть, можно добавить логику позже

    # Получаем общее количество
    total = query.count()

    # Сортировка по дедлайну (сначала ближайшие)
    query = query.order_by(
        Task.deadline.asc().nulls_last(),
        Task.created_at.desc()
    )

    # Пагинация
    tasks = query.offset(filters.skip).limit(filters.limit).all()

    return tasks, total


def update_task(
        db: Session,
        task_id: int,
        task_update,
        user_id: Optional[int] = None
):
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


def complete_task(db: Session, task_id: int, user_id: Optional[int] = None):
    """
    Отметить задачу как выполненную
    """
    db_task = get_task_by_id(db, task_id, user_id)
    if not db_task:
        return None

    from ..model import enums  # ← относительный импорт

    db_task.status = enums.TaskStatus.COMPLETED
    # db_task.updated_at = datetime.utcnow()  # Если добавите поле в модель

    db.commit()
    db.refresh(db_task)
    return db_task


def get_user_tasks_count(db: Session, user_id: int) -> dict:
    """
    Получение статистики по задачам пользователя
    """
    from .. import schemes  # ← относительный импорт
    from ..model import Task, enums  # ← относительный импорт

    total = db.query(Task).filter(Task.user_id == user_id).count()
    completed = db.query(Task).filter(
        Task.user_id == user_id,
        Task.status == enums.TaskStatus.COMPLETED
    ).count()
    assigned = db.query(Task).filter(
        Task.user_id == user_id,
        Task.status == enums.TaskStatus.ASSIGNED
    ).count()

    # Задачи с дедлайном (опционально)
    with_deadline = db.query(Task).filter(
        Task.user_id == user_id,
        Task.deadline.isnot(None)
    ).count()

    return {
        "total": total,
        "completed": completed,
        "assigned": assigned,
        "with_deadline": with_deadline,
        "completion_rate": completed / total if total > 0 else 0
    }