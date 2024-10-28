#  Содержание bot.py

from telebot import types, apihelper
from logger import logger, log_function_call


def register_handlers(signal_bot):
    """
    Регистрирует все необходимые обработчики для бота.

    Этот метод добавляет обработчики для команд, различных типов сообщений,
    редактированных сообщений и нажатий на инлайн-кнопки.

    Args:
        signal_bot (telebot.TeleBot): Экземпляр бота, для которого регистрируются обработчики.
    """

    @log_function_call
    @signal_bot.message_handler(func=lambda message: message.text[1:].lower() and message.text.startswith('/'))
    def command_message(message):
        """
        Обрабатывает команды, начинающиеся с '/' (например, /start, /help).

        В зависимости от команды, отправляет соответствующее сообщение пользователю.

        Args:
            message (telebot.types.Message): Объект сообщения от пользователя.
        """
        user_id = message.from_user.id
        command = message.text[1:].lower()
        logger.info(f"Пользователь {user_id} отправил команду /{command}")

        if command == "start":
            signal_bot.send_message(
                message.chat.id, "Привет! Я бот, который помогает с торговыми сигналами."
            )
        elif command == "help":
            signal_bot.send_message(
                message.chat.id,
                "Список доступных команд:\n/start - Начать работу\n/help - Помощь"
            )
        else:
            signal_bot.send_message(
                message.chat.id, "Команда не распознана. Введите /help для списка команд."
            )

    @log_function_call
    @signal_bot.message_handler(content_types=[
        'text', 'photo', 'audio', 'document', 'video',
        'video_note', 'voice', 'sticker', 'animation'
    ])
    def handle_all_messages(message):
        """
        Обрабатывает все входящие сообщения различных типов.

        В зависимости от типа контента сообщения, отправляет соответствующий ответ.

        Args:
            message (telebot.types.Message): Объект сообщения от пользователя.
        """
        user_id = message.from_user.id
        content_type = message.content_type
        logger.info(
            f"Пользователь {user_id} отправил сообщение типа {content_type}")

        response_messages = {
            'text': f"Вы отправили текстовое сообщение: {message.text}",
            'photo': "Вы отправили фото!",
            'audio': "Вы отправили аудио!",
            'document': "Вы отправили документ!",
            'video': "Вы отправили видео!",
            'video_note': "Вы отправили видеосообщение!",
            'voice': "Вы отправили голосовое сообщение!",
            'sticker': "Вы отправили стикер!",
            'animation': "Вы отправили анимацию!"
        }

        response = response_messages.get(
            content_type, "Неизвестный тип сообщения.")
        try:
            signal_bot.send_message(message.chat.id, response)
        except apihelper.ApiException as e:
            logger.error(
                f"Ошибка при отправке сообщения пользователю {user_id}: {e}")

    @log_function_call
    @signal_bot.edited_message_handler(content_types=[
        'text', 'photo', 'audio', 'document', 'video',
        'video_note', 'voice', 'sticker', 'animation'
    ])
    def handle_edited_messages(message):
        """
        Обрабатывает редактированные сообщения различных типов.

        В зависимости от типа контента редактированного сообщения, отправляет соответствующий ответ.

        Args:
            message (telebot.types.Message): Объект редактированного сообщения от пользователя.
        """
        user_id = message.from_user.id
        content_type = message.content_type
        logger.info(
            f"Пользователь {user_id} отредактировал сообщение типа {content_type}")

        response_messages = {
            'text': f"Вы отредактировали текстовое сообщение: {message.text}",
            'photo': "Вы отредактировали фото!",
            'audio': "Вы отредактировали аудио!",
            'document': "Вы отредактировали документ!",
            'video': "Вы отредактировали видео!",
            'video_note': "Вы отредактировали видеосообщение!",
            'voice': "Вы отредактировали голосовое сообщение!",
            'sticker': "Вы отредактировали стикер!",
            'animation': "Вы отредактировали анимацию!"
        }

        response = response_messages.get(
            content_type, "Вы отредактировали сообщение неизвестного типа.")
        try:
            signal_bot.send_message(message.chat.id, response)
        except apihelper.ApiException as e:
            logger.error(
                f"Ошибка при отправке сообщения пользователю {user_id}: {e}")

    @log_function_call
    @signal_bot.callback_query_handler(func=lambda call: True)
    def handle_inline_buttons(call):
        """
        Обрабатывает нажатия на инлайн-кнопки.

        В зависимости от данных, отправленных с кнопкой, выполняет соответствующее действие.

        Args:
            call (telebot.types.CallbackQuery): Объект вызова обратного вызова от нажатия кнопки.
        """
        user_id = call.from_user.id
        logger.info(
            f"Пользователь {user_id} нажал инлайн-кнопку с данными: {call.data}")

        responses = {
            "some_action": "Вы выбрали действие!",
            "another_action": "Другое действие выполнено!"
        }

        response = responses.get(call.data, "Неизвестное действие.")
        try:
            signal_bot.answer_callback_query(call.id, response)
        except apihelper.ApiException as e:
            logger.error(
                f"Ошибка при ответе на обратный вызов пользователю {user_id}: {e}")

    @log_function_call
    @signal_bot.message_handler(content_types=[
        "new_chat_members", "left_chat_member", "new_chat_photo", "delete_chat_photo",
        "group_chat_created", "supergroup_chat_created", "channel_chat_created",
        "migrate_to_chat_id", "migrate_from_chat_id", "pinned_message"
    ])
    def handle_service_messages(message):
        """
        Обрабатывает служебные сообщения чата.

        В зависимости от типа служебного сообщения, выполняет соответствующие действия,
        такие как приветствие новых участников или информирование о покидании чата.

        Args:
            message (telebot.types.Message): Объект служебного сообщения от чата.
        """
        user_id = message.from_user.id if message.from_user else None
        content_type = message.content_type

        if content_type == "new_chat_members":
            for member in message.new_chat_members:
                logger.info(f"Пользователь {member.id} присоединился к чату")
                try:
                    signal_bot.send_message(
                        message.chat.id, f"Привет, {member.first_name}!"
                    )
                except apihelper.ApiException as e:
                    logger.error(
                        f"Ошибка при приветствии пользователя {member.id}: {e}")
        elif content_type == "left_chat_member":
            logger.info(
                f"Пользователь {message.left_chat_member.id} покинул чат")
            try:
                signal_bot.send_message(
                    message.chat.id, f"{message.left_chat_member.first_name} покинул нас."
                )
            except apihelper.ApiException as e:
                logger.error(
                    f"Ошибка при уведомлении о покидании пользователя {message.left_chat_member.id}: {e}")
        elif content_type == "pinned_message":
            pinned_text = message.pinned_message.text if message.pinned_message else "Нет текста."
            logger.info(f"Сообщение закреплено в чате: {pinned_text}")
        else:
            logger.info(f"Служебное сообщение: {content_type}")
