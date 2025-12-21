
import os
from datetime import datetime

import pytz
from dotenv import load_dotenv
load_dotenv()

# Конфигурация сервера
APP_PATH = "app.main:app"
HOST = "0.0.0.0"
PORT = 8000
RELOAD = True
LOG_LEVEL = "info"

# HOST = os.getenv("HOST", "127.0.0.1")
# PORT = int(os.getenv("PORT", 8000))
# RELOAD = os.getenv("RELOAD", "True").lower() == "true"
# LOG_LEVEL = os.getenv("LOG_LEVEL", "info")

# JWT конфигурация
SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-key-change-in-production")
ALGORITHM = os.getenv("ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 90))

# Временная зона
MOSCOW_TZ = pytz.timezone('Europe/Moscow')
def getServerTime() -> datetime:
    return datetime.now(MOSCOW_TZ)

# Директория для логов
LOG_DIR = "logs"
# Сколько дней хранить логи
LOG_RETENTION_DAYS = 30
# Формат даты в имени файла
DATE_FORMAT = "%Y-%m-%d"
# Формат времени в записях логов
TIME_FORMAT = "%Y-%m-%d %H:%M:%S"

# @classmethod
def get_log_dir(cls):
    """Получить путь к директории логов"""
    if not os.path.exists(cls.LOG_DIR):
        os.makedirs(cls.LOG_DIR)
    return cls.LOG_DIR

# @classmethod
def get_daily_log_file(cls):
    """Получить путь к файлу логов за текущий день"""
    log_dir = cls.get_log_dir()
    current_date = datetime.now().strftime(cls.DATE_FORMAT)
    return os.path.join(log_dir, f"errors_{current_date}.log")

# @classmethod
def get_general_log_file(cls):
    """Получить путь к общему файлу логов"""
    log_dir = cls.get_log_dir()
    return os.path.join(log_dir, "errors_all.log")

# @classmethod
def get_timestamp(cls):
    """Получить текущую метку времени"""
    return datetime.now().strftime(cls.TIME_FORMAT)