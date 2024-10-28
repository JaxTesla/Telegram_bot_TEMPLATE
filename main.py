# Содержание main.py

import telebot
import json
import threading
from datetime import datetime
import time
import sys
from logger import logger
from watchdog_monitoring import start_watchdog

# Переменные для мониторинга и перезапуска
bot_update_types = [
    "message", "edited_message", "channel_post", "edited_channel_post", "inline_query", "chosen_inline_result",
    "callback_query", "shipping_query", "pre_checkout_query", "poll", "poll_answer", "my_chat_member", "chat_member",
    "chat_join_request",
]

file_list = ['main.py', 'logger.py', 'bot.py',
             'watchdog_monitoring.py']  # Список файлов для мониторинга


def load_bot_token():
    '''Функция для загрузки токена'''
    logger.info("Загрузка токена бота")
    with open('settings/key.json', 'r') as file:
        config = json.load(file)
    return config['tgm_bots']['SendingTradeSignal_Bot']['tgm_bot_token']


def run_bot_polling(signal_bot, max_retries=5, base_delay=5):
    """
    Функция для запуска infinity_polling в отдельном потоке с обработкой ошибок и ограничением на количество повторных попыток.

    Args:
        signal_bot (telebot.TeleBot): Экземпляр бота, используемый для polling.
        max_retries (int): Максимальное количество попыток переподключения.
        base_delay (int): Начальная задержка перед переподключением, в секундах.
    """
    retry_count = 0
    delay = base_delay

    while retry_count < max_retries:
        try:
            logger.info("Запуск infinity_polling для бота")
            signal_bot.infinity_polling(
                timeout=5,
                long_polling_timeout=5,
                allowed_updates=bot_update_types,
                skip_pending=False
            )
            break  # Успешный запуск - выходим из цикла
        except Exception as e:
            retry_count += 1
            logger.error(
                f"Ошибка в работе бота: {e}. Попытка {retry_count} из {max_retries}")
            if retry_count >= max_retries:
                logger.error(
                    "Достигнуто максимальное количество попыток. Бот остановлен.")
                break
            # Экспоненциальная задержка с увеличением интервала
            time.sleep(delay)
            # Ограничиваем задержку максимум до 60 секунд
            delay = min(delay * 2, 60)

    if retry_count >= max_retries:
        logger.error(
            "Не удалось восстановить соединение. Остановка работы бота.")


def run_signal_bot(stop_event, restart_event):
    """Запуск бота и обработка остановки."""
    logger.info(f"{datetime.now()} Запуск бота - signal_bot")
    bot_token = load_bot_token()
    signal_bot = telebot.TeleBot(bot_token)

    from bot import register_handlers
    register_handlers(signal_bot)
    logger.info("Бот инициализирован и обработчики зарегистрированы")

    # Запуск infinity_polling в отдельном потоке
    polling_thread = threading.Thread(
        target=run_bot_polling, args=(signal_bot,))
    polling_thread.start()

    try:
        while not stop_event.is_set():
            time.sleep(1)
            if restart_event.is_set():
                logger.info("Перезапуск бота по событию restart_event")
                stop_event.set()  # Ставим событие для остановки

    except Exception as e:
        logger.error(
            f"Ошибка при перезапуске бота по событию restart_event: {e}")
    finally:
        logger.info("Вызов stop_polling() для завершения работы бота")
        signal_bot.stop_polling()
        polling_thread.join()  # Ожидание завершения потока polling
        logger.info("Бот остановлен и поток polling завершен.")


if __name__ == "__main__":
    logger.info("-- Запуск телеграм бота --")
    try:
        while True:
            logger.info(
                "Создание событий stop_event и restart_event для новой итерации")
            stop_event = threading.Event()
            restart_event = threading.Event()

            # Запуск watchdog в отдельном потоке
            thread_watchdog = threading.Thread(
                target=start_watchdog, args=(file_list, restart_event, stop_event), daemon=True)
            thread_watchdog.start()
            logger.info("Watchdog поток запущен")

            # Запуск бота
            thread_bot = threading.Thread(
                target=run_signal_bot, args=(stop_event, restart_event))
            thread_bot.start()
            logger.info("Бот поток запущен")

            # Ожидание сигналов
            while not stop_event.is_set() and not restart_event.is_set():
                time.sleep(1)

            if restart_event.is_set():
                logger.info(
                    "Получен сигнал перезапуска (restart_event). Устанавливаем stop_event для остановки бота.")
                stop_event.set()

            logger.info("Ожидание завершения потоков bot и watchdog")
            thread_bot.join()
            thread_watchdog.join()

            if stop_event.is_set() and not restart_event.is_set():
                logger.info(
                    "Остановка работы бота по сигналу stop_event без перезапуска")
                break

            if restart_event.is_set():
                logger.info("Перезапуск бота.")
                continue

    except KeyboardInterrupt:
        logger.info("Завершение работы по CTRL+C.")
        stop_event.set()
        restart_event.set()

        logger.info("Ожидание завершения потоков bot и watchdog после CTRL+C")
        thread_bot.join()
        thread_watchdog.join()
        sys.exit(0)

    logger.info("Работа программы завершена.")
