import uvicorn
import sys
import os

# Получаем абсолютный путь к корню проекта
project_root = os.path.dirname(os.path.abspath(__file__))

# Добавляем папку backend в путь Python
backend_path = os.path.join(project_root, 'backend')
sys.path.insert(0, backend_path)

try:
    from app.core import config as cfg
except ImportError as e:
    # Попробуем другой путь
    sys.path.insert(0, project_root)
    from backend.app.core import config as cfg


def main():
    print("\n" + "="*50)
    print("[START] Запуск Homework Tracker...")
    print(f"[START] Хост: {cfg.HOST}")
    print(f"[START] Порт: {cfg.PORT}")
    print(f"[START] Путь к приложению: {cfg.APP_PATH}")
    print(f"[START] Документация: http://{cfg.HOST}:{cfg.PORT}/api/docs")
    print("="*50)

    # Запускаем сервер
    uvicorn.run(cfg.APP_PATH,  # путь к приложению
                host = cfg.HOST,  # доступно со всех интерфейсов
                port = cfg.PORT,  # порт
                reload = cfg.RELOAD,  # авто-перезагрузка при изменении кода
                log_level = cfg.LOG_LEVEL,  # уровень логирования
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