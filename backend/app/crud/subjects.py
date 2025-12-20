# backend/app/crud/subjects.py
from sqlalchemy.orm import Session
from typing import List, Optional
from ..core.config import getServerTime, MOSCOW_TZ


def create_subject(db: Session, subject, user_id: int):
    """
    Создание нового предмета
    """
    from ..model import Subject
    db_subject = Subject(**subject.model_dump(), user_id=user_id)
    db.add(db_subject)
    db.commit()
    db.refresh(db_subject)
    return db_subject


def get_subject_by_id(db: Session, subject_id: int, user_id: Optional[int] = None):
    """
    Получение предмета по ID
    """
    from ..model import Subject
    query = db.query(Subject).filter(Subject.id == subject_id)
    if user_id:
        query = query.filter(Subject.user_id == user_id)
    return query.first()


def get_user_subjects(db: Session, user_id: int):
    """
    Получение всех предметов пользователя
    """
    from ..model import Subject
    return db.query(Subject).filter(Subject.user_id == user_id).all()


def update_subject(
        db: Session,
        subject_id: int,
        subject_update,
        user_id: Optional[int] = None
):
    """
    Обновление предмета
    """
    db_subject = get_subject_by_id(db, subject_id, user_id)
    if not db_subject:
        return None

    update_data = subject_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_subject, field, value)

    db.commit()
    db.refresh(db_subject)
    return db_subject


def delete_subject(db: Session, subject_id: int, user_id: Optional[int] = None) -> bool:
    """
    Удаление предмета
    """
    db_subject = get_subject_by_id(db, subject_id, user_id)
    if not db_subject:
        return False

    db.delete(db_subject)
    db.commit()
    return True

def delete_all_subjects(db: Session, user_id: Optional[int] = None) -> bool:
    """
    Удаление всех предметов текущего user
    """
    subjects = get_user_subjects(db, user_id)
    if not subjects:
        return False
    try:
        for subject in subjects:
            db.delete(subject)
            db.commit()
    except:
        print("ошибка удаления!")
        return False
    return True


def get_subject_stats(db: Session, subject_id: int, user_id: int):
    """
    Получение статистики по предмету
    """
    from . import tasks as crud_tasks
    from ..schemes import TaskFilter

    # Получаем все задачи для предмета
    filters = TaskFilter(subject_id=subject_id, limit=1000)
    tasks, _ = crud_tasks.get_tasks(db, user_id, filters, include_overdue=False)
    subjects = get_user_subjects(db, user_id)
    curSubject = get_subject_by_id(db, subject_id, user_id)

    # Считаем статистику
    totalTasks = len(tasks)
    totalSubjects = len(subjects)
    completed = sum(1 for task in tasks if task.status == "completed")
    assigned = totalTasks - completed

    # Задачи с дедлайном
    with_deadline = sum(1 for task in tasks if task.deadline is not None)

    # Просроченные задачи - правильно сравниваем
    now = getServerTime()  # aware datetime с часовым поясом Москвы

    overdue = 0
    for task in tasks:
        if (task.status == "assigned" and
                task.deadline is not None):

            # Приводим deadline к тому же часовому поясу
            if task.deadline.tzinfo is None:
                # Если deadline без часового пояса, считаем что это Москва
                deadline_localized = MOSCOW_TZ.localize(task.deadline)
            else:
                # Если есть часовой пояс, конвертируем в Москву
                deadline_localized = task.deadline.astimezone(MOSCOW_TZ)

            if deadline_localized < now:
                overdue += 1

    return {
        "subject_id": subject_id,
        "total_subjects": totalSubjects,
        "total_tasks": totalTasks,
        "completed": completed,
        "assigned": assigned,
        "with_deadline": with_deadline,
        "overdue": overdue,
        "completion_rate": (completed / totalTasks * 100) if totalTasks > 0 else 0,
        "created_at": curSubject.created_at,
    }