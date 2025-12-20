from pydantic import BaseModel, EmailStr, Field, ConfigDict, field_validator
from datetime import datetime
from typing import Optional, List
from enum import Enum

# ==================== ENUMS ====================

class TaskStatus(str, Enum):
    """Статусы задач"""
    ASSIGNED = "assigned"       # задано (ответ на задание не отправлено)
    COMPLETED = "completed"     # выполнено

class TaskPriority(str, Enum):
    """Приоритеты задач"""
    LOW = "low"                 # низкий
    MEDIUM = "medium"           # средний
    HIGH = "high"               # высокий

# ==================== USER SCHEMAS ====================

class UserBase(BaseModel):
    """Базовая схема пользователя"""
    email: EmailStr
    login: str = Field(..., min_length=3, max_length=50)
    name: str = Field(..., min_length=2, max_length=100)
    groupName: Optional[str] = Field(None, max_length=100)

class UserCreate(UserBase):
    """Схема для создания пользователя"""
    password: str = Field(..., min_length=8, max_length=72)

class UserLogin(BaseModel):
    """Схема для входа в систему"""
    login: str
    password: str

class UserResponse(UserBase):
    """Схема ответа с пользователем (без пароля)"""
    id: int
    is_active: bool
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

# ==================== SUBJECT SCHEMAS ====================

class SubjectBase(BaseModel):
    """Базовая схема предмета"""
    name: str = Field(..., min_length=1, max_length=100)

class SubjectCreate(SubjectBase):
    """Схема для создания предмета"""
    pass

class SubjectResponse(SubjectBase):
    """Схема ответа с предметом"""
    id: int
    user_id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

# ==================== TASK SCHEMAS ====================

class TaskBase(BaseModel):
    """Базовая схема задания"""
    title: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = None
    priority: TaskPriority = TaskPriority.MEDIUM
    deadline: Optional[datetime] = None

class TaskCreate(TaskBase):
    """Схема для создания задания"""
    subject_id: int

class TaskUpdate(BaseModel):
    """Схема для обновления задания (все поля опциональны)"""
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = None
    status: Optional[TaskStatus] = None
    priority: Optional[TaskPriority] = None
    deadline: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)

class TaskResponse(TaskBase):
    """Схема ответа с заданием"""
    id: int
    user_id: int
    subject_id: int
    status: TaskStatus = TaskStatus.ASSIGNED
    created_at: datetime
    # updated_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)

# ==================== COMPOSITE RESPONSE SCHEMAS ====================

class TaskWithSubjectResponse(TaskResponse):
    """Задание с информацией о предмете"""
    subject_name: str
    # subject_color: str

class SubjectWithTasksResponse(SubjectResponse):
    """Предмет со списком заданий"""
    tasks: List[TaskResponse] = []

class UserWithTasksResponse(UserResponse):
    """Пользователь со списком заданий"""
    tasks: List[TaskResponse] = []

# ==================== API RESPONSE SCHEMAS ====================

class Token(BaseModel):
    """Схема для JWT токена"""
    access_token: str
    token_type: str

class TokenData(BaseModel):
    """Данные внутри JWT токена"""
    user_id: Optional[int] = None

class HealthCheckResponse(BaseModel):
    """Схема для проверки здоровья API"""
    status: str
    database: dict
    timestamp: str

class ErrorResponse(BaseModel):
    """Схема для ошибок API"""
    detail: str
    error_code: Optional[str] = None

# ==================== FILTER SCHEMAS ====================

class TaskFilter(BaseModel):
    """Схема для фильтрации заданий"""
    status: Optional[TaskStatus] = None
    priority: Optional[TaskPriority] = None
    subject_id: Optional[int] = None
    search: Optional[str] = None
    skip: int = 0
    limit: int = 100

class PaginationResponse(BaseModel):
    """Схема для пагинации"""
    total: int
    skip: int
    limit: int
    has_more: bool

class TaskListResponse(BaseModel):
    """Схема для списка заданий с пагинацией"""
    tasks: List[TaskWithSubjectResponse]
    pagination: PaginationResponse

# ================ RESET PASSWORD ====================

class ForgotPasswordRequest(BaseModel):
    """Схема для запроса восстановления пароля"""
    email: EmailStr

class ResetPasswordTokenRequest(BaseModel):
    """Схема для сброса пароля через токен"""
    token: str
    new_password: str = Field(..., min_length=8, max_length=72)
    confirm_password: str = Field(..., min_length=8, max_length=72)

    @field_validator('confirm_password')
    @classmethod
    def passwords_match(cls, v, info):
        if 'new_password' in info.data and v != info.data['new_password']:
            raise ValueError('Пароли не совпадают')
        return v

class ResetPasswordRequest(BaseModel):
    """Схема для сброса пароля без токена"""
    new_password: str = Field(..., min_length=8, max_length=72)
    confirm_password: str = Field(..., min_length=8, max_length=72)

    @field_validator('confirm_password')
    @classmethod
    def passwords_match(cls, v, info):
        if 'new_password' in info.data and v != info.data['new_password']:
            raise ValueError('Пароли не совпадают')
        return v


class UserStatsOverview(BaseModel):
    """Общая статистика пользователя"""
    total_tasks: int
    completed_tasks: int
    assigned_tasks: int
    overdue_tasks: int
    total_subjects: int
    productivity_score: int
    completion_rate: float
    priority_stats: Optional[dict] = None

class SubjectStat(BaseModel):
    """Статистика по предмету"""
    subject_id: int
    subject_name: str
    subject_color: str
    total_tasks: int
    completed_tasks: int
    completion_rate: int

class RecentActivity(BaseModel):
    """Недавняя активность"""
    last_week_tasks: int
    last_week_completed: int
    daily_average: float

class UserStatsResponse(BaseModel):
    """Полная статистика пользователя"""
    overview: UserStatsOverview
    subject_stats: List[SubjectStat]
    recent_activity: RecentActivity

    model_config = ConfigDict(from_attributes=True)

class TaskStatusUpdate(BaseModel):
    status: TaskStatus  # "assigned" или "completed"