import uvicorn
import sys
import os

# Получаем абсолютный путь к корню проекта
project_root = os.path.dirname(os.path.abspath(__file__))

# Добавляем папку backend в путь Python
backend_path = os.path.join(project_root, 'backend')
sys.path.insert(0, backend_path)

# print(f"[DEBUG] Project root: {project_root}")
# print(f"[DEBUG] Backend path: {backend_path}")
# print(f"[DEBUG] Python path: {sys.path}")

try:
    from app.core import config as cfg
    print("[DEBUG] Import successful!")
except ImportError as e:
    print(f"[DEBUG] Import error: {e}")
    # Попробуем другой путь
    sys.path.insert(0, project_root)
    from backend.app.core import config as cfg


def main():
    """Запускает сервер"""
    print("\n" + "="*50)
    print("[START] Запуск Homework Tracker...")
    print(f"[START] Хост: {cfg.host}")
    print(f"[START] Порт: {cfg.port}")
    print(f"[START] Путь к приложению: {cfg.app_path}")
    print(f"[START] Документация: http://{cfg.host}:{cfg.port}/api/docs")
    print("="*50)

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
        print("\n[STOP] Сервер остановлен")
    except Exception as e:
        print(f"\n[ERROR] Ошибка запуска: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)