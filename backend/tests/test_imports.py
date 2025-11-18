# tests/test_simple.py
def test_imports():
    """Просто проверяем что импорты работают"""
    try:
        from app.models import User
        from app.database import Base
        assert True  # Если дошли сюда - все ок!
    except ImportError as e:
        assert False, f"Import failed: {e}"