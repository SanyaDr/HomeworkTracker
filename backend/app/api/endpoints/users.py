# backend/app/api/endpoints/users.py
from fastapi import APIRouter, Depends, HTTPException, status, Response, BackgroundTasks, Request
from fastapi.security import OAuth2PasswordRequestForm
from jose import jwt, JWTError
from pydantic import EmailStr
from sqlalchemy.orm import Session
from datetime import timedelta

from ...core import config as cfg
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
        response: Response,
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
    # Устанавливаем токен в куки
    response.set_cookie(
        key="access_token",
        value=f"Bearer {access_token}",
        httponly=True,  # Не доступен через JavaScript (защита от XSS)
        max_age=ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        expires=ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        samesite="lax",
        # secure = cfg.ENVIRONMENT == "production",  # True только в production
        secure = cfg.SECURE_COOKIE,
        path="/"
    )

    return {"access_token": access_token, "token_type": "bearer"}

@router.get("/authStatus")
def auth_status(request: Request, db: Session = Depends(get_db)):
    """
    Проверка авторизации через куки.
    Всегда возвращает 200 с флагом authenticated.
    """
    # Берем токен из куки напрямую
    token_cookie = request.cookies.get("access_token")

    # Если нет куки - сразу возвращаем false
    if not token_cookie:
        return {"authenticated": False, "user": None}
    # Убираем "Bearer " префикс если есть
    token = token_cookie
    if token.startswith("Bearer "):
        token = token[7:]

    # Проверяем токен
    try:
        from ...core import config
        from jose import jwt

        payload = jwt.decode(token, config.SECRET_KEY, algorithms=[config.ALGORITHM])
        user_id = payload.get("sub")

        if not user_id:
            return {"authenticated": False, "user": None}

        # Получаем пользователя из БД
        user = crud_users.get_user_by_id(db, int(user_id))

        if not user:
            return {"authenticated": False, "user": None}

        return {
            "authenticated": True,
            "user": {
                "id": user.id,
                "login": user.login,
                "name": user.name,
                "email": user.email
            }
        }

    except Exception:
        # Любая ошибка - считаем не авторизованным
        return {"authenticated": False, "user": None}



@router.post("/logout")
def logout(response: Response):
    """
    Выход из системы (удаление cookies)
    """
    response.delete_cookie(key="access_token", path="/")
    return {"message": "Logged out successfully"}

@router.get("/profile", response_model=schemes.UserResponse)
def read_users_me(
        current_user: schemes.UserResponse = Depends(get_current_user)):
    """
    Получение информации о текущем пользователе
    """
    return current_user


@router.put("/profile", response_model=schemes.UserResponse)
def update_user_me(
        user_update: schemes.UserBase,
        db: Session = Depends(get_db),
        current_user: schemes.UserResponse = Depends(get_current_user)):
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
        current_user: schemes.UserResponse = Depends(get_current_user)):
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

@router.delete("/data")
def delete_all_user_data(
        db: Session = Depends(get_db),
        current_user: schemes.UserResponse = Depends(get_current_user)):
    """
    Удаление всех данных текущего пользователя
    """
    from ...crud.subjects import delete_all_subjects
    success = delete_all_subjects(db, current_user.id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    return {"message": "User data deleted successfully"}

@router.post("/forgot-password")
async def forgot_password(
        request: schemes.ForgotPasswordRequest,
        background_tasks: BackgroundTasks,
        db: Session = Depends(get_db)):
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
    reset_url = f"http://{cfg.HOST}:{cfg.PORT}/reset-password?token={reset_token}"

    # Отправляем email (в production)
    # TODO: реализовать отправку email
    # background_tasks.add_task(send_reset_email, email, reset_url)

    # Для разработки просто логируем
    print(f"[PASSWORD RESET] User: {user.login}, Reset URL: {reset_url}")

    return {
        "message": "Инструкции по восстановлению пароля отправлены на email",
        "debug_url": reset_url  # TODO: Вывод токена сброса пароля: Удалить в production!
    }



@router.post("/reset-password")
async def reset_password(
        request: schemes.ResetPasswordTokenRequest,
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

@router.post("/profile/changePassword")
def changePassword(
        request: schemes.ResetPasswordRequest,
        current_user: schemes.UserResponse = Depends(get_current_user),
        db: Session = Depends(get_db),
):
    """
    Сброс пароля без токена
    """
    try:
        # Находим пользователя
        user = crud_users.get_user_by_id(db, current_user.id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )

        # Обновляем пароль
        updated_user = crud_users.update_user(
            db,
            current_user.id,
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



@router.get("/stats")
def get_user_stats(
        db: Session = Depends(get_db),
        current_user: schemes.UserResponse = Depends(get_current_user),
):
    """
    Получение статистики пользователя
    """
    from ...crud import tasks as crud_tasks, subjects as crud_subjects

    # Используем существующую функцию из tasks
    tasks_stats = crud_tasks.get_user_tasks_stats(db, current_user.id)

    # Получаем все предметы пользователя
    subjects = crud_subjects.get_user_subjects(db, current_user.id)

    # Рассчитываем статистику по предметам через общую функцию
    subject_stats = []
    for subject in subjects:
        stats = crud_subjects.get_subject_stats(db, subject.id, current_user.id)

        subject_stats.append({
            "subject_id": subject.id,
            "subject_name": subject.name,
            "total_tasks": stats["total_tasks"],
            "completed_tasks": stats["completed"],
            "completion_rate": stats["completion_rate"],
            "inProcess_tasks": stats["total_tasks"] - stats["completed"],
            "created_at": stats["created_at"],
        })

    # Активность за последнюю неделю - исправляем сравнение дат
    from ...schemes import TaskFilter

    now = cfg.getServerTime()  # aware datetime с часовым поясом Москвы
    last_week = now - timedelta(days=7)

    filters = TaskFilter(limit=1000)
    all_tasks, _ = crud_tasks.get_tasks(db, current_user.id, filters, include_overdue=False)

    # Правильно сравниваем даты с учетом часовых поясов
    recent_tasks = []
    for task in all_tasks:
        if task.created_at is not None:
            # Приводим created_at к московскому времени для сравнения
            if task.created_at.tzinfo is None:
                # Если created_at без часового пояса, считаем что это Москва
                created_at_localized = cfg.MOSCOW_TZ.localize(task.created_at)
            else:
                # Если есть часовой пояс, конвертируем в Москву
                created_at_localized = task.created_at.astimezone(cfg.MOSCOW_TZ)

            if created_at_localized >= last_week:
                recent_tasks.append(task)

    # Серия дней подряд (упрощенная версия)
    streak_days = calculate_streak_days(all_tasks)

    return {
        "overview": {
            "total_tasks": tasks_stats["total"],
            "completed_tasks": tasks_stats["completed"],
            "assigned_tasks": tasks_stats["assigned"],
            "overdue_tasks": tasks_stats["overdue"],
            "total_subjects": len(subjects),
            "productivity_score": int(tasks_stats["completion_rate"] * 100),
            "streak_days": streak_days,
            "priority_stats": tasks_stats.get("priority_stats", {})
        },
        "subject_stats": subject_stats,
        "recent_activity": {
            "last_week_tasks": len(recent_tasks),
            "last_week_completed": len([t for t in recent_tasks if t.status == "completed"]),
            "daily_average": round(len(recent_tasks) / 7, 1) if recent_tasks else 0
        }
    }



def calculate_streak_days(tasks) -> int:
    """
    Рассчитывает сколько дней подряд пользователь добавлял/выполнял задания
    Упрощенная версия - проверяем активность по созданию заданий
    """
    if not tasks:
        return 0

    # Собираем уникальные даты активности
    activity_dates = set()
    for task in tasks:
        if task.created_at is not None:
            if task.created_at.tzinfo is None:
                created_at = cfg.MOSCOW_TZ.localize(task.created_at)
            else:
                created_at = task.created_at.astimezone(cfg.MOSCOW_TZ)
            activity_dates.add(created_at.date())

    if not activity_dates:
        return 0

    # Сортируем даты
    sorted_dates = sorted(activity_dates, reverse=True)

    now = cfg.getServerTime()
    today = now.date()

    # Проверяем, была ли активность сегодня
    streak = 0
    if sorted_dates[0] == today:
        streak = 1

        # Проверяем предыдущие дни
        from datetime import timedelta
        check_date = today - timedelta(days=1)
        for date in sorted_dates[1:]:
            if date == check_date:
                streak += 1
                check_date -= timedelta(days=1)
            else:
                break

    return streak

