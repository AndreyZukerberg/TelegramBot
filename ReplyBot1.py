import logging
import os
import shutil
from telethon import TelegramClient, events
from telethon.tl.types import MessageMediaPhoto, MessageMediaDocument

# Настройка логирования
logging.basicConfig(level=logging.INFO)

# Установите параметры своего клиента
api_id = 20382465  # ваш api_id
api_hash = "a83e9c7539fd0f8294b7b3b02796c90a"  # ваш api_hash
phone_number = "+380713626583"  # ваш номер телефона

# Настройка клиента Telethon
client = TelegramClient('shest_bot', api_id, api_hash)

# Канал источника и канал назначения
source_channel = 'https://t.me/expltgk'
target_channel = 'https://t.me/ShestDonetsk'

# Функция для отправки сообщений
async def send_message_with_media(message):
    try:
        media_files = []

        # Если сообщение содержит фотографии
        if isinstance(message.media, MessageMediaPhoto):
            # Скачиваем фото
            file_path = await client.download_media(message.media, "./downloads/")
            logging.info(f"Скачан файл: {file_path}")
            media_files.append(file_path)
        
        # Если сообщение содержит документ (например, PDF, архив)
        elif isinstance(message.media, MessageMediaDocument):
            # Скачиваем документ
            file_path = await client.download_media(message.media, "./downloads/")
            logging.info(f"Скачан файл: {file_path}")
            media_files.append(file_path)

        # Отправляем файлы в целевой канал
        if media_files:
            await client.send_file(target_channel, media_files, caption=message.text)
            logging.info(f"Сообщение отправлено в канал {target_channel}")

        # Удаляем скачанные файлы
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

    # Пересылаем сообщение с медиа
    await send_message_with_media(message)


# Запуск клиента
async def main():
    await client.start(phone_number)
    logging.info("Бот запущен.")
    await client.run_until_disconnected()

# Запуск программы
if __name__ == "__main__":
    client.loop.run_until_complete(main())