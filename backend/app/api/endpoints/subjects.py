from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

# Импорты с относительными путями
from ... import schemes
from ...crud import subjects as crud_subjects
from ...core.database import get_db
from ...core.auth import get_current_user
from ...core.config import getServerTime

router = APIRouter(prefix="/subjects", tags=["subjects"])


@router.post("/", response_model=schemes.SubjectResponse)
def create_subject(
        subject: schemes.SubjectCreate,
        db: Session = Depends(get_db),
        current_user: schemes.UserResponse = Depends(get_current_user)
):
    """
    Создание нового предмета
    """
    # Проверяем уникальность названия предмета для пользователя
    existing_subjects = crud_subjects.get_user_subjects(db, current_user.id)
    for subj in existing_subjects:
        if subj.name.lower() == subject.name.lower():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Subject with this name already exists"
            )

    return crud_subjects.create_subject(db, subject, current_user.id)


@router.get("/", response_model=List[schemes.SubjectResponse])
def get_subjects(
        db: Session = Depends(get_db),
        current_user: schemes.UserResponse = Depends(get_current_user)
):
    """
    Получение всех предметов пользователя
    """
    return crud_subjects.get_user_subjects(db, current_user.id)


@router.get("/{subject_id}", response_model=schemes.SubjectResponse)
def get_subject(
        subject_id: int,
        db: Session = Depends(get_db),
        current_user: schemes.UserResponse = Depends(get_current_user)
):
    """
    Получение предмета по ID
    """
    subject = crud_subjects.get_subject_by_id(db, subject_id, current_user.id)
    if not subject:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Subject not found"
        )
    return subject


@router.put("/{subject_id}", response_model=schemes.SubjectResponse)
def update_subject(
        subject_id: int,
        subject_update: schemes.SubjectBase,
        db: Session = Depends(get_db),
        current_user: schemes.UserResponse = Depends(get_current_user)
):
    """
    Обновление предмета
    """
    subject = crud_subjects.update_subject(
        db, subject_id, subject_update, current_user.id
    )
    if not subject:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Subject not found"
        )
    return subject


@router.delete("/{subject_id}")
def delete_subject(
        subject_id: int,
        db: Session = Depends(get_db),
        current_user: schemes.UserResponse = Depends(get_current_user)
):
    """
    Удаление предмета
    """
    success = crud_subjects.delete_subject(db, subject_id, current_user.id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Subject not found"
        )
    return {"message": "Subject deleted successfully"}


@router.get("/{subject_id}/tasks", response_model=List[schemes.TaskResponse])
def get_subject_tasks(
        subject_id: int,
        db: Session = Depends(get_db),
        current_user: schemes.UserResponse = Depends(get_current_user)
):
    """
    Получение всех задач для конкретного предмета
    """
    from ...crud import tasks as crud_tasks

    # Проверяем что предмет существует и принадлежит пользователю
    subject = crud_subjects.get_subject_by_id(db, subject_id, current_user.id)
    if not subject:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Subject not found"
        )

    # Получаем задачи для этого предмета
    from ...schemes import TaskFilter
    filters = TaskFilter(subject_id=subject_id, limit=100)
    tasks, _ = crud_tasks.get_tasks(db, current_user.id, filters)

    return tasks


@router.get("/{subject_id}/stats")
def get_subject_stats(
        subject_id: int,
        db: Session = Depends(get_db),
        current_user: schemes.UserResponse = Depends(get_current_user)
):
    """
    Получение статистики по предмету
    """
    from ...crud import tasks as crud_tasks

    # Проверяем что предмет существует
    subject = crud_subjects.get_subject_by_id(db, subject_id, current_user.id)
    if not subject:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Subject not found"
        )

    # Получаем все задачи для предмета
    from ...schemes import TaskFilter
    filters = TaskFilter(subject_id=subject_id, limit=1000)
    tasks, _ = crud_tasks.get_tasks(db, current_user.id, filters)

    # Считаем статистику
    total = len(tasks)
    completed = sum(1 for task in tasks if task.status == "completed")
    assigned = total - completed

    # Задачи с дедлайном
    with_deadline = sum(1 for task in tasks if task.deadline is not None)

    # Просроченные задачи
    now = getServerTime()
    overdue = sum(1 for task in tasks
                  if task.status == "assigned"
                  and task.deadline
                  and task.deadline < now)

    return {
        "subject_id": subject_id,
        "subject_name": subject.name,
        "total_tasks": total,
        "completed": completed,
        "assigned": assigned,
        "with_deadline": with_deadline,
        "overdue": overdue,
        "completion_rate": (completed / total * 100) if total > 0 else 0
    }