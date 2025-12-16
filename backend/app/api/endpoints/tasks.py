from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from typing import List, Optional

from ...core.database import get_db
from ...crud import tasks as crud_tasks
from ... import schemes
from ...core.auth import get_current_user

router = APIRouter(prefix="/tasks", tags=["tasks"])


@router.post("/", response_model=schemes.TaskResponse)
def create_task(
        task: schemes.TaskCreate,
        db: Session = Depends(get_db),
        current_user: schemes.UserResponse = Depends(get_current_user)
):
    """
    Создание новой задачи
    """
    # Проверка существования предмета
    from app.crud import subjects as crud_subjects
    subject = crud_subjects.get_subject_by_id(db, task.subject_id, current_user.id)
    if not subject:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Subject not found"
        )

    db_task = crud_tasks.create_task(db, task, current_user.id)
    return db_task


@router.get("/", response_model=schemes.TaskListResponse)
def get_tasks(
        status: Optional[schemes.TaskStatus] = Query(None),
        priority: Optional[schemes.TaskPriority] = Query(None),
        subject_id: Optional[int] = Query(None),
        search: Optional[str] = Query(None),
        skip: int = Query(0, ge=0),
        limit: int = Query(100, ge=1, le=200),
        db: Session = Depends(get_db),
        current_user: schemes.UserResponse = Depends(get_current_user)
):
    """
    Получение списка задач с фильтрацией
    """
    filters = schemes.TaskFilter(
        status=status,
        priority=priority,
        subject_id=subject_id,
        search=search,
        skip=skip,
        limit=limit
    )

    db_tasks, total = crud_tasks.get_tasks(db, current_user.id, filters)

    # Преобразуем задачи в схему с информацией о предмете
    tasks_with_subjects = []
    for task in db_tasks:
        task_dict = schemes.TaskResponse.model_validate(task).model_dump()
        task_dict["subject_name"] = task.subject.name
        task_dict["subject_color"] = task.subject.color
        tasks_with_subjects.append(
            schemes.TaskWithSubjectResponse(**task_dict)
        )

    return schemes.TaskListResponse(
        tasks=tasks_with_subjects,
        pagination=schemes.PaginationResponse(
            total=total,
            skip=skip,
            limit=limit,
            has_more=(skip + len(db_tasks)) < total
        )
    )


@router.get("/{task_id}", response_model=schemes.TaskWithSubjectResponse)
def get_task(
        task_id: int,
        db: Session = Depends(get_db),
        current_user: schemes.UserResponse = Depends(get_current_user)
):
    """
    Получение задачи по ID
    """
    db_task = crud_tasks.get_task_by_id(db, task_id, current_user.id)
    if not db_task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )

    # Преобразуем в схему с информацией о предмете
    task_dict = schemes.TaskResponse.model_validate(db_task).model_dump()
    task_dict["subject_name"] = db_task.subject.name
    task_dict["subject_color"] = db_task.subject.color

    return schemes.TaskWithSubjectResponse(**task_dict)


@router.put("/{task_id}", response_model=schemes.TaskResponse)
def update_task(
        task_id: int,
        task_update: schemes.TaskUpdate,
        db: Session = Depends(get_db),
        current_user: schemes.UserResponse = Depends(get_current_user)
):
    """
    Обновление задачи
    """
    db_task = crud_tasks.update_task(db, task_id, task_update, current_user.id)
    if not db_task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )
    return db_task


@router.delete("/{task_id}")
def delete_task(
        task_id: int,
        db: Session = Depends(get_db),
        current_user: schemes.UserResponse = Depends(get_current_user)
):
    """
    Удаление задачи
    """
    success = crud_tasks.delete_task(db, task_id, current_user.id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )
    return {"message": "Task deleted successfully"}


@router.patch("/{task_id}/complete", response_model=schemes.TaskResponse)
def complete_task(
        task_id: int,
        db: Session = Depends(get_db),
        current_user: schemes.UserResponse = Depends(get_current_user)
):
    """
    Отметить задачу как выполненную
    """
    db_task = crud_tasks.complete_task(db, task_id, current_user.id)
    if not db_task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )
    return db_task


@router.get("/stats/summary")
def get_tasks_summary(
        db: Session = Depends(get_db),
        current_user: schemes.UserResponse = Depends(get_current_user)
):
    """
    Получение статистики по задачам
    """
    stats = crud_tasks.get_user_tasks_stats(db, current_user.id)

    return stats