# backend/app/api/endpoints/users.py
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from datetime import timedelta

from ...core.database import get_db
from ...crud import users as crud_users
from ... import schemes
from ...core.auth import (
    authenticate_user,
    create_access_token,
    get_current_user,
    ACCESS_TOKEN_EXPIRE_MINUTES
)

router = APIRouter(prefix="/users", tags=["users"])


@router.post("/", response_model=schemes.UserResponse)
def create_user(
        user: schemes.UserCreate,
        db: Session = Depends(get_db)
):
    """
    Регистрация нового пользователя
    """
    # Проверка уникальности логина
    db_user = crud_users.get_user_by_login(db, user.login)
    if db_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Login already registered"
        )

    # Проверка уникальности email
    db_user = crud_users.get_user_by_email(db, user.email)
    if db_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )

    return crud_users.create_user(db, user)


@router.post("/login", response_model=schemes.Token)
def login(
        form_data: OAuth2PasswordRequestForm = Depends(),
        db: Session = Depends(get_db)
):
    """
    Аутентификация пользователя
    """
    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect login or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": str(user.id)},
        expires_delta=access_token_expires
    )

    return {"access_token": access_token, "token_type": "bearer"}


@router.get("/me", response_model=schemes.UserResponse)
def read_users_me(
        current_user: schemes.UserResponse = Depends(get_current_user)
):
    """
    Получение информации о текущем пользователе
    """
    return current_user


@router.put("/me", response_model=schemes.UserResponse)
def update_user_me(
        user_update: schemes.UserBase,
        db: Session = Depends(get_db),
        current_user: schemes.UserResponse = Depends(get_current_user)
):
    """
    Обновление данных текущего пользователя
    """
    updated_user = crud_users.update_user(
        db,
        current_user.id,
        user_update.model_dump(exclude_unset=True),
        exclude_fields=["password"]
    )

    if not updated_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    return updated_user


@router.delete("/me")
def delete_user_me(
        db: Session = Depends(get_db),
        current_user: schemes.UserResponse = Depends(get_current_user)
):
    """
    Удаление текущего пользователя
    """
    success = crud_users.delete_user(db, current_user.id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    return {"message": "User deleted successfully"}