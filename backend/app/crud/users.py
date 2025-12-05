from sqlalchemy.orm import Session
from typing import Optional
from app.model import enums, models
from passlib.context import CryptContext
from app import schemes

# Для хеширования паролей
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Проверка пароля"""
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """Хеширование пароля"""
    return pwd_context.hash(password)


def get_user_by_id(db: Session, user_id: int) -> Optional[models.User]:
    """Получение пользователя по ID"""
    return db.query(models.User).filter(models.User.id == user_id).first()


def get_user_by_login(db: Session, login: str) -> Optional[models.User]:
    """Получение пользователя по логину"""
    return db.query(models.User).filter(models.User.login == login).first()


def get_user_by_email(db: Session, email: str) -> Optional[models.User]:
    """Получение пользователя по email"""
    return db.query(models.User).filter(models.User.email == email).first()


def create_user(db: Session, user: schemes.UserCreate) -> models.User:
    """Создание нового пользователя"""
    hashed_password = get_password_hash(user.password)
    db_user = models.User(
        **user.model_dump(exclude={"password"}),
        hashed_password=hashed_password
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def authenticate_user(db: Session, login: str, password: str) -> Optional[models.User]:
    """Аутентификация пользователя"""
    user = get_user_by_login(db, login)
    if not user:
        return None
    if not verify_password(password, user.hashed_password):
        return None
    return user


def update_user(
        db: Session,
        user_id: int,
        user_update: dict,
        exclude_fields: list = ["password"]
) -> Optional[models.User]:
    """Обновление данных пользователя"""
    db_user = get_user_by_id(db, user_id)
    if not db_user:
        return None

    # Если обновляется пароль
    if "password" in user_update and "password" not in exclude_fields:
        user_update["hashed_password"] = get_password_hash(user_update.pop("password"))

    for field, value in user_update.items():
        if field not in exclude_fields and hasattr(db_user, field):
            setattr(db_user, field, value)

    db.commit()
    db.refresh(db_user)
    return db_user


def delete_user(db: Session, user_id: int) -> bool:
    """Удаление пользователя"""
    db_user = get_user_by_id(db, user_id)
    if not db_user:
        return False

    db.delete(db_user)
    db.commit()
    return True