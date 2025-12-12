# backend/app/core/auth.py

import os
from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from fastapi import Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from .database import get_db
from .. import schemes
from . import config

# Конфигурация JWT
SECRET_KEY = config.SECRET_KEY
ALGORITHM = config.ALGORITHM
ACCESS_TOKEN_EXPIRE_MINUTES = config.ACCESS_TOKEN_EXPIRE_MINUTES

# Схема для заголовка Authorization (auto_error=False чтобы не падать сразу)
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/users/login", auto_error=False)


def get_token_from_cookie(request: Request) -> Optional[str]:
    """
    Извлекает токен из cookies
    """
    token = request.cookies.get("access_token")
    if token:
        # Убираем "Bearer " префикс если есть
        if token.startswith("Bearer "):
            token = token[7:]
    return token

async def get_token(
        request: Request,
        token: str = Depends(oauth2_scheme)
) -> Optional[str]:
    """
    Получает токен: сначала из cookies, потом из заголовка Authorization
    """
    cookie_token = get_token_from_cookie(request)
    return cookie_token or token


async def get_current_user(
        request: Request,
        token: str = Depends(get_token),
        db: Session = Depends(get_db)
) -> schemes.UserResponse:
    """
    Получение текущего пользователя по токену.
    """
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )

    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    from app.crud import users as crud_users

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get("sub")
        if user_id is None:
            raise credentials_exception

        token_data = schemes.TokenData(user_id=int(user_id))
        user = crud_users.get_user_by_id(db, user_id=token_data.user_id)

        if user is None:
            raise credentials_exception

        return schemes.UserResponse.model_validate(user)

    except JWTError:
        raise credentials_exception


# Остальные функции остаются без изменений
def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)

    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def authenticate_user(db: Session, username: str, password: str):
    from app.crud import users as crud_users
    return crud_users.authenticate_user(db, username, password)