import os
import shutil
import logging
import asyncio
from telethon import TelegramClient, events
from telethon.tl.types import MessageMediaPhoto

# Настройка логирования
logging.basicConfig(level=logging.INFO)

# Установите параметры своего клиента
api_id = 20382465  # ваш api_id
api_hash = "a83e9c7539fd0f8294b7b3b02796c90a"  # ваш api_hash
phone_number = "+380713626583"  # ваш номер телефона

# Настройка клиента Telethon
client = TelegramClient('shest_bot', api_id, api_hash)

# Канал источника и канал назначения
source_channel = 'expltgk'  # Источник (название канала без https://t.me/)
target_channel = 'ShestDonetsk'  # Цель (название канала без https://t.me/)

# Функция для скачивания медиафайлов
async def download_media(message):
    media_files = []
    try:
        # Проверка на медиафайл
        if isinstance(message.media, MessageMediaPhoto):
            file_path = await client.download_media(message.media, "./downloads/")
            logging.info(f"Скачан файл: {file_path}")
            media_files.append(file_path)

        # Для случая, если несколько медиафайлов
        if message.media and hasattr(message.media, 'photos'):
            for photo in message.media.photos:
                file_path = await client.download_media(photo, "./downloads/")
                logging.info(f"Скачано фото: {file_path}")
                media_files.append(file_path)

    except Exception as e:
        logging.error(f"Ошибка при скачивании медиа: {str(e)}")
    
    return media_files


# Функция для отправки медиа и текста в целевой канал
async def send_message_with_media(message, media_files):
    try:
        logging.info("Подготовка к отправке сообщения с медиафайлами...")
        
        # Пауза для того, чтобы файлы успели загрузиться
        await asyncio.sleep(2)

        # Логируем перед отправкой
        logging.info(f"Готовим {len(media_files)} медиафайлов для отправки в канал {target_channel}.")
        logging.debug(f"Список файлов для отправки: {media_files}")

        # Проверка на то, что media_files не пустой
        if media_files:
            if isinstance(media_files, list) and len(media_files) > 0:
                try:
                    logging.info(f"Отправка {len(media_files)} медиафайлов в канал {target_channel}.")
                    await client.send_file(target_channel, files=media_files, caption=message.text, force_document=False)
                    logging.info(f"Сообщение отправлено в канал {target_channel}.")
                except Exception as e:
                    logging.error(f"Ошибка при пересылке файлов: {str(e)}")
            else:
                logging.error("Ошибка: media_files не содержит файлов или не является списком.")
        else:
            logging.warning("media_files пустой список.")

        # Пауза для уверенности, что сообщения отправлены
        await asyncio.sleep(2)

        # Удаляем скачанные файлы
        logging.info(f"Удаление файлов: {media_files}")
        for file in media_files:
            if os.path.exists(file):
                os.remove(file)
                logging.info(f"Удален файл: {file}")
            else:
                logging.warning(f"Файл не найден для удаления: {file}")

        # Удаляем папку с загруженными файлами
        if os.path.exists('./downloads/'):
            shutil.rmtree('./downloads/')
            logging.info("Удалена папка ./downloads/")

    except Exception as e:
        logging.error(f"Ошибка при пересылке сообщения: {str(e)}")


# Обработчик новых сообщений
@client.on(events.NewMessage(chats=source_channel))
async def handler(event):
    message = event.message
    logging.info(f"Получено сообщение от {source_channel}: {message.id}")

    # Скачиваем все медиафайлы из сообщения
    media_files = await download_media(message)

    # Пауза перед отправкой сообщения
    await asyncio.sleep(1)

    # Пересылаем сообщение с текстом и медиа
    await send_message_with_media(message, media_files)


# Запуск клиента
async def main():
    await client.start(phone_number)
    logging.info("Бот запущен.")
    await client.run_until_disconnected()

# Запуск программы
if __name__ == "__main__":
    client.loop.run_until_complete(main())