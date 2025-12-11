from fastapi import Request

def get_templates(request: Request):
    """Получаем templates из состояния приложения"""
    return request.app.state.templates