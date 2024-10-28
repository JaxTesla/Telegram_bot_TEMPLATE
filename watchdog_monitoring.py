#  Содержание watchdog_monitoring.py

import os
import time
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from logger import logger  # Импортируем логгер из `logger.py`


class WatchdogHandler(FileSystemEventHandler):
    """
    Обработчик событий для мониторинга изменений в файлах.

    Этот класс наследует `FileSystemEventHandler` из библиотеки `watchdog`
    и используется для отслеживания изменений в указанных файлах. При
    обнаружении изменения в одном из файлов из списка `file_list`, устанавливается
    событие `restart_event` для инициирования перезапуска бота.

    Атрибуты:
        file_list (list): Список имен файлов, за изменениями которых необходимо следить.
        restart_event (threading.Event): Событие, которое устанавливается при обнаружении изменения.
    """
    def __init__(self, file_list, restart_event):
        """
        Инициализирует WatchdogHandler.

        Args:
            file_list (list): Список имен файлов для мониторинга.
            restart_event (threading.Event): Событие для установки при обнаружении изменения.
        """
        super().__init__()
        self.file_list = file_list
        self.restart_event = restart_event

    def on_modified(self, event):
        """
        Обрабатывает событие изменения файла.

        При изменении файла проверяет, входит ли он в `file_list`. Если да,
        записывает информацию в лог и устанавливает событие `restart_event`.

        Args:
            event (FileSystemEvent): Объект события, содержащий информацию об изменении.
        """
        filename = os.path.basename(event.src_path)
        if filename in self.file_list:
            logger.info(
                f"Изменение в файле: {event.src_path}. Устанавливается restart_event")
            self.restart_event.set()


def start_watchdog(file_list, restart_event, stop_event):
    """
    Запускает мониторинг файлов с использованием watchdog.

    Эта функция инициализирует `WatchdogHandler` для отслеживания изменений
    в файлах из `file_list` и запускает наблюдателя (`Observer`). В цикле
    она продолжает работу до тех пор, пока не будет установлено событие `stop_event`
    или `restart_event`. После завершения работы наблюдателя записывает соответствующее сообщение в лог.

    Args:
        file_list (list): Список имен файлов для мониторинга.
        restart_event (threading.Event): Событие, устанавливаемое при обнаружении изменения.
        stop_event (threading.Event): Событие для остановки мониторинга.
    """
    event_handler = WatchdogHandler(file_list, restart_event)
    observer = Observer()
    observer.schedule(event_handler, path=".", recursive=False)
    observer.start()
    logger.info("Watchdog запущен для мониторинга изменений")

    try:
        while not stop_event.is_set() and not restart_event.is_set():
            time.sleep(1)
    finally:
        observer.stop()
        observer.join()
        logger.info("Watchdog остановлен.")
