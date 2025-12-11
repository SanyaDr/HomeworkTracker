"""
CRUD операции для работы с базой данных
"""

# Список того, что будет доступно при импорте из этого пакета
__all__ = [
    # users
    "get_user_by_id",
    "get_user_by_login",
    "get_user_by_email",
    "create_user",
    "authenticate_user",
    "update_user",
    "delete_user",
    "verify_password",
    "get_password_hash",

    # tasks
    "create_task",
    "get_task_by_id",
    "get_tasks",
    "update_task",
    "delete_task",
    "complete_task",
    "get_user_tasks_count",

    # subjects
    "create_subject",
    "get_subject_by_id",
    "get_user_subjects",
    "update_subject",
    "delete_subject",
]
