#  Содержание watchdog_monitoring.py

import os
import time
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from logger import logger  # Импортируем логгер из `logger.py`


class WatchdogHandler(FileSystemEventHandler):
    def __init__(self, file_list, restart_event):
        super().__init__()
        self.file_list = file_list
        self.restart_event = restart_event

    def on_modified(self, event):
        filename = os.path.basename(event.src_path)
        if filename in self.file_list:
            logger.info(
                f"Изменение в файле: {event.src_path}. Устанавливается restart_event")
            self.restart_event.set()


def start_watchdog(file_list, restart_event, stop_event):
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
