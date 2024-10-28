#  Содержание logger.py

import logging
from logging.handlers import RotatingFileHandler
from functools import wraps
import os

# Путь к директории логов
LOG_DIR = r"f:\code\logs\TGM_Pattern"
LOG_FILE = os.path.join(LOG_DIR, "bot_log.log")

# Создаем директорию для логов, если она не существует
os.makedirs(LOG_DIR, exist_ok=True)


# Настройка логгера
def setup_logger(name='bot_logger'):
    """
    Настраивает и возвращает логгер с указанным именем.

    Этот логгер настроен для вывода логов как в файл с ротацией,
    так и в консоль. Ротация файлов происходит при достижении
    размера 50 МБ, при этом сохраняется до 5 резервных файлов.

    Args:
        name (str): Имя логгера. По умолчанию 'bot_logger'.

    Returns:
        logging.Logger: Настроенный экземпляр логгера.
    """

    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)

    # Хендлер для вывода логов в файл с ротацией
    file_handler = RotatingFileHandler(
        LOG_FILE,
        maxBytes=50 * 1024 * 1024,  # Ротация при достижении 50 МБ
        backupCount=5,               # Хранить до 5 резервных файлов
        encoding='utf-8'
    )
    file_handler.setFormatter(logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'))

    # Хендлер для вывода логов в терминал
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'))

    # Добавляем хендлеры к логгеру, если они еще не добавлены
    # if not logger.handlers:
    if not logger.hasHandlers():
        logger.addHandler(file_handler)
        logger.addHandler(console_handler)

    return logger


# Инициализируем основной логгер
logger = setup_logger()


# Декоратор для логирования вызова функции
def log_function_call(func):
    """
    Декоратор для логирования вызовов функций.

    При декорировании функции этот декоратор автоматически
    записывает в лог информацию о вызове функции, включая
    имя функции, переданные позиционные и именованные аргументы.

    Args:
        func (callable): Функция, которую необходимо декорировать.

    Returns:
        callable: Обёрнутая функция с добавленным логированием.
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        logger.info(
            f"Вызов функции {func.__name__} с аргументами: {args} и именованными аргументами: {kwargs}")
        return func(*args, **kwargs)
    return wrapper
