import logging
import os
from telethon import TelegramClient, events
from telethon.tl.types import MessageMediaPhoto, MessageMediaDocument

# Настройки
api_id = 20382465
api_hash = "a83e9c7539fd0f8294b7b3b02796c90a"
phone_number = "+380713626583"

# Каналы
source_channel = 'expltgk'
target_channel = 'ShestDonetsk'

# Логирование
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Создание клиента
client = TelegramClient(phone_number, api_id, api_hash)

@client.on(events.NewMessage(chats=source_channel))
async def forward_message(event):
    """Пересылка сообщений с сохранением и отправкой всех медиафайлов в одном посте."""
    try:
        media_files = []
        temp_dir = "temp_media"

        if not os.path.exists(temp_dir):
            os.makedirs(temp_dir)

        # Скачивание медиафайлов
        if event.message.media:
            if isinstance(event.message.media, (MessageMediaPhoto, MessageMediaDocument)):
                file_path = await event.message.download_media(file=temp_dir)
                media_files.append(file_path)

        # Отправка медиафайлов одним постом
        if media_files:
            await client.send_file(target_channel, media_files, caption=event.message.text or "")
            
            # Удаление файлов после отправки
            for file in media_files:
                os.remove(file)

            logger.info(f"Сообщение с медиа переслано из {source_channel} в {target_channel}")
        else:
            await client.send_message(target_channel, event.message.text)
            logger.info(f"Текстовое сообщение переслано из {source_channel} в {target_channel}")

    except Exception as e:
        logger.error(f"Ошибка при пересылке сообщения: {e}")

async def main():
    """Запуск бота."""
    try:
        logger.info("Бот запущен")
        await client.start(phone_number)
        await client.run_until_disconnected()
    except Exception as e:
        logger.error(f"Ошибка при запуске бота: {e}")

# Запуск клиента
client.loop.run_until_complete(main())