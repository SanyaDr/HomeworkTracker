"""
Модели базы данных
"""

# Импортируем перечисления
from .enums import TaskStatus, TaskPriority

# Импортируем модели
from .models import Base, User, Subject, Task

# Группируем для удобства
# models = {
#     "User": User,
#     "Subject": Subject,
#     "Task": Task,
#     "Base": Base,
# }
#
# enums = {
#     "TaskStatus": TaskStatus,
#     "TaskPriority": TaskPriority,
# }

# Экспортируем всё явно
__all__ = [
    "Base",
    "User",
    "Subject",
    "Task",
    "TaskStatus",
    "TaskPriority",
]