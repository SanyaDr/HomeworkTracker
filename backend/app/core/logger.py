# backend/app/core/logger.py
import traceback
# from datetime import datetime
import os

from .config import getServerTime

def log_error(error: Exception, context: str = ""):
    """Самая простая версия с разделением по датам"""
    try:
        # Создаем папку logs если нет
        if not os.path.exists("logs"):
            os.makedirs("logs")

        # Файл с текущей датой
        today = getServerTime().strftime("%Y-%m-%d")
        log_file = f"logs/errors_{today}.log"

        # Формируем запись
        now = getServerTime().strftime("%Y-%m-%d %H:%M:%S")

        log_entry = f"[{now}] "
        if context:
            log_entry += f"{context} - "
        log_entry += f"{type(error).__name__}: {str(error)}\n"
        log_entry += f"Трассировка:\n{traceback.format_exc()}\n"
        log_entry += "-" * 60 + "\n"

        # Записываем
        with open(log_file, "a", encoding="utf-8") as f:
            f.write(log_entry)

        print(f"Ошибка записана в {log_file}")
    except:
        print("Не удалось записать лог")

def log_message(message: str, error_type: str = "ERROR"):
    try:
        log_dir = "logs"
        if not os.path.exists(log_dir):
            os.makedirs(log_dir)

        log_file = os.path.join(log_dir, "errors.log")

        timestamp = getServerTime().strftime("%Y-%m-%d %H:%M:%S")
        error_message = f"[{timestamp}] {error_type}: {message}\n"

        with open(log_file, "a", encoding="utf-8") as f:
            f.write(error_message)

    except:
        pass


def cleanup_old_logs(days_to_keep: int = 30):
    """
    Очистка старых лог-файлов
    """
    try:
        from datetime import datetime, timedelta
        import glob

        log_dir = "logs"
        if not os.path.exists(log_dir):
            return

        # Рассчитываем дату, старше которой удаляем
        cutoff_date = datetime.now() - timedelta(days=days_to_keep)

        # Ищем все файлы errors_*.log
        log_files = glob.glob(os.path.join(log_dir, "errors_*.log"))

        for log_file in log_files:
            try:
                # Извлекаем дату из имени файла
                filename = os.path.basename(log_file)
                if filename.startswith("errors_") and filename.endswith(".log"):
                    date_str = filename[7:-4]  # "errors_YYYY-MM-DD.log"

                    # Пробуем распарсить дату
                    file_date = datetime.strptime(date_str, "%Y-%m-%d")

                    # Если файл старше указанного периода - удаляем
                    if file_date < cutoff_date:
                        os.remove(log_file)
                        print(f"Удален старый лог-файл: {log_file}")

            except (ValueError, IndexError):
                # Если не удалось распарсить дату - пропускаем
                continue

    except Exception as e:
        print(f"Ошибка при очистке логов: {e}")