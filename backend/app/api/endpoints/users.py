# backend/app/api/endpoints/users.py
from fastapi import APIRouter, Depends, HTTPException, status, Response, BackgroundTasks
from fastapi.security import OAuth2PasswordRequestForm
from jose import jwt, JWTError
from pydantic import EmailStr
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

## Конфиг для отправки email
# email_config = ConnectionConfig(
#     MAIL_USERNAME="your-email@gmail.com",
#     MAIL_PASSWORD="your-password",
#     MAIL_FROM="noreply@tasktracker.ru",
#     MAIL_PORT=587,
#     MAIL_SERVER="smtp.gmail.com",
#     MAIL_STARTTLS=True,
#     MAIL_SSL_TLS=False,
#     USE_CREDENTIALS=True
# )


router = APIRouter(prefix="/users", tags=["users"])


# Регистрация пользователя
@router.post("/register", response_model=schemes.UserResponse)
def create_user(
        user: schemes.UserCreate,
        db: Session = Depends(get_db)
):
    print("Зашел в create_user")
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
    print("прошел проверки create_user")
    return crud_users.create_user(db, user)


@router.post("/login", response_model=schemes.Token)
def login(
        response: Response,
        form_data: OAuth2PasswordRequestForm = Depends(),
        db: Session = Depends(get_db)
):
    """
    Аутентификация пользователя
    """
    print("зашел в post login endpoints/users")
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
    print("Начал ставить куки")
    # Устанавливаем токен в куки
    response.set_cookie(
        key="access_token",
        value=f"Bearer {access_token}",
        httponly=True,  # Не доступен через JavaScript (защита от XSS)
        max_age=ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        expires=ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        samesite="lqax",
        secure=False
    )

    return {"access_token": access_token, "token_type": "bearer"}


@router.get("/profile", response_model=schemes.UserResponse)
def read_users_me(
        current_user: schemes.UserResponse = Depends(get_current_user)
):
    """
    Получение информации о текущем пользователе
    """
    return current_user


@router.put("/profile", response_model=schemes.UserResponse)
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


@router.delete("/profile")
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


@router.post("/forgot-password")
async def forgot_password(
        request: schemes.ForgotPasswordRequest,
        background_tasks: BackgroundTasks,
        db: Session = Depends(get_db)
):
    """
    Отправка ссылки для восстановления пароля
    """
    email = request.email
    # Проверяем, существует ли пользователь с таким email
    user = crud_users.get_user_by_email(db, email)
    if not user:
        return {
            "message": "Аккаунт с таким email не зарегистрирован"
        }

    # Генерируем токен для сброса пароля
    reset_token = create_access_token(
        data={"sub": str(user.id), "type": "password_reset"},
        expires_delta=timedelta(hours=24)  # Токен действует 24 часа
    )

    # Создаем URL для сброса пароля
    from ...core import config as cfg
    reset_url = f"http://{cfg.host}:{cfg.port}/reset-password?token={reset_token}"

    # Отправляем email (в production)
    # TODO: реализуй отправку email
    # background_tasks.add_task(send_reset_email, email, reset_url)

    # Для разработки просто логируем
    print(f"[PASSWORD RESET] User: {user.login}, Reset URL: {reset_url}")

    return {
        "message": "Инструкции по восстановлению пароля отправлены на email",
        "debug_url": reset_url  # TODO: Удалить в production!
    }



@router.post("/reset-password")
async def reset_password(
        request: schemes.ResetPasswordRequest,
        db: Session = Depends(get_db)
):
    """
    Сброс пароля по токену
    """
    from ...core import config as cfg
    try:
        # Проверяем токен
        payload = jwt.decode(
            request.token,
            cfg.SECRET_KEY,
            algorithms=[cfg.ALGORITHM]
        )

        # Проверяем тип токена
        if payload.get("type") != "password_reset":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid token type"
            )

        user_id = int(payload.get("sub"))

        # Находим пользователя
        user = crud_users.get_user_by_id(db, user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )

        # Обновляем пароль
        updated_user = crud_users.update_user(
            db,
            user_id,
            {"password": request.new_password},
            exclude_fields=[]
        )

        if not updated_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to update password"
            )

        return {
            "message": "Пароль успешно изменен"
        }

    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired token"
        )