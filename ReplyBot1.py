import logging
import os
from telethon import TelegramClient, events

# Настройки API
api_id = 20382465
api_hash = "a83e9c7539fd0f8294b7b3b02796c90a"
phone_number = "+380713626583"

# Каналы
source_channel = "expltgk"
target_channel = "ShestDonetsk"

# Логирование
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Создание клиента
client = TelegramClient(phone_number, api_id, api_hash)

@client.on(events.NewMessage(chats=source_channel))
async def forward_message(event):
    """Пересылка сообщений с сохранением всех медиафайлов в одном посте."""
    try:
        media_files = []
        temp_dir = "temp_media"

        if not os.path.exists(temp_dir):
            os.makedirs(temp_dir)

        # Проверяем, является ли сообщение частью альбома
        if event.message.grouped_id:
            grouped_id = event.message.grouped_id
            messages = await event.client.get_messages(source_channel, limit=20)
            album_messages = [msg for msg in messages if msg.grouped_id == grouped_id]

            for msg in album_messages:
                if msg.media:
                    file_path = await msg.download_media(file=temp_dir)
                    if file_path:
                        media_files.append(file_path)

        else:  # Одиночное сообщение
            if event.message.media:
                file_path = await event.message.download_media(file=temp_dir)
                if file_path:
                    media_files.append(file_path)

        # Проверяем, есть ли медиафайлы перед отправкой
        if media_files:
            await client.send_file(target_channel, media=media_files, caption=event.message.text or "")
            
            # Удаление файлов после отправки
            for file in media_files:
                os.remove(file)

            logger.info(f"Сообщение с медиа переслано из {source_channel} в {target_channel}")
        else:
            await client.send_message(target_channel, event.message.text or "")
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