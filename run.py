"""
Точка входа для запуска сервера Homework Tracker
"""
import uvicorn
import sys
import os
from app.core import startConfig as cfg

# Добавляем папку backend в путь Python
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

def main():
    """Запускает сервер"""
    print("[START] Запуск Homework Tracker...")
    print("[START] Текущая директория:", os.getcwd())
    print("[START] API доступно по: http://localhost:8000")
    print("[START] Для остановки нажмите Ctrl+C")

    # Запускаем сервер
    uvicorn.run(cfg.app_path,                   # путь к приложению
                host = cfg.host,                # доступно со всех интерфейсов
                port = cfg.port,                # порт
                reload = cfg.reload,            # авто-перезагрузка при изменении кода
                log_level = cfg.log_level,      # уровень логирования
                )

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nСервер остановлен")
    except Exception as e:
        print(f"Ошибка запуска: {e}")
        sys.exit(1)