import os
from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from .database import get_db
from .. import schemes
from . import startConfig

# Конфигурация JWT
SECRET_KEY = startConfig.SECRET_KEY
ALGORITHM = startConfig.ALGORITHM
ACCESS_TOKEN_EXPIRE_MINUTES = startConfig.ACCESS_TOKEN_EXPIRE_MINUTES

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/users/login")


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """
    Создание JWT токена
    """
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)

    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def verify_token(token: str, credentials_exception):
    """
    Верификация JWT токена
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get("sub")
        if user_id is None:
            raise credentials_exception
        return schemes.TokenData(user_id=int(user_id))
    except JWTError:
        raise credentials_exception


async def get_current_user(
        token: str = Depends(oauth2_scheme),
        db: Session = Depends(get_db)
) -> schemes.UserResponse:
    """
    Получение текущего пользователя по токену
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    from app.crud import users as crud_users
    token_data = verify_token(token, credentials_exception)
    user = crud_users.get_user_by_id(db, user_id=token_data.user_id)
    if user is None:
        raise credentials_exception

    return schemes.UserResponse.model_validate(user)


def authenticate_user(db: Session, username: str, password: str):
    """
    Аутентификация пользователя
    """
    from app.crud import users as crud_users
    return crud_users.authenticate_user(db, username, password)
