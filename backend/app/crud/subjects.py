from sqlalchemy.orm import Session
from typing import List, Optional

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