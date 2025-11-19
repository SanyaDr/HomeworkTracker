from enum import Enum

class TaskStatus(str, Enum):
    """Статусы задач"""
    ASSIGNED = "assigned"       # задано (ответ на задание не отправлено)
    COMPLETED = "completed"     # выполнено

class TaskPriority(str, Enum):
    """Приоритеты задач"""
    LOW = "low"                 # низкий
    MEDIUM = "medium"           # средний
    HIGH = "high"               # высокий