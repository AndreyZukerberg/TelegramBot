import logging
from telethon import TelegramClient, events
from telethon.tl.functions.messages import SendMediaRequest
from telethon.tl.types import InputPeerChannel
import re

# Настройки
api_id = 20382465
api_hash = "a83e9c7539fd0f8294b7b3b02796c90a"
phone_number = "+380713626583"

# Каналы источники и целевые каналы
channel_mapping = {
    'https://t.me/+QUo4lv3MKq04Yjk6': '@Piterburg24na7',
    '@chp_donetska': '@ShestDonetsk',
    '@moscowach': '@MosNevSlp',
    '@mash_siberia': '@ShestNovosib',
    '@e1_news': '@ShestEKB',
    '@kazancity': '@ShestKazan',
    '@incidentkld': '@ShestKaliningrad',
    '@etorostov': '@ShestRostov',
    '@moynizhny': '@ShestNN',
    '@expltgk': '@ShestDonetsk',  # Все каналы получают посты от @expltgk
    '@naebnet': '@NoTrustNet'
}

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

client = TelegramClient(phone_number, api_id, api_hash)

async def send_message(client, target_channel, text, media=None):
    """Отправка сообщения в канал с медиа."""
    try:
        if media:
            # Отправка медиа файлов, отправляем сразу все медиа в одном сообщении
            logger.info(f"Отправка сообщения с медиа в канал {target_channel}")
            await client.send_message(target_channel, text=text, media=media)
        else:
            # Отправка только текста
            logger.info(f"Отправка сообщения в канал {target_channel}")
            await client.send_message(target_channel, text=text)
    except Exception as e:
        logger.error(f"Ошибка при отправке сообщения в канал {target_channel}: {e}")

async def handle_message(event, source_channel):
    """Обрабатывает входящие сообщения и пересылает их в целевые каналы."""
    try:
        message = event.message
        logger.info(f"Получено сообщение от канала {source_channel}.")

        # Пересылка в целевой канал
        target_channel = channel_mapping.get(source_channel)
        if target_channel:
            # Пересылаем в целевой канал
            if message.media:
                # Отправка медиа в одном сообщении
                await send_message(client, target_channel, message.text, media=message.media)
            else:
                # Отправка только текста
                await send_message(client, target_channel, message.text)
        else:
            logger.warning(f"Не найден целевой канал для источника {source_channel}.")
    except Exception as e:
        logger.error(f"Ошибка при обработке сообщения от канала {source_channel}: {e}")

@client.on(events.NewMessage())
async def forward_message(event):
    """Обрабатывает новые сообщения от указанных каналов источников."""
    try:
        source_channel = event.chat_id  # Используем chat_id для получения канала
        logger.info(f"Новое сообщение от канала {source_channel}")

        # Проверка, что сообщение пришло от одного из источников
        if str(source_channel) in channel_mapping.keys():
            await handle_message(event, source_channel)
        else:
            logger.info(f"Сообщение не из одного из отслеживаемых каналов: {source_channel}")
    except Exception as e:
        logger.error(f"Ошибка при обработке нового сообщения: {e}")

async def main():
    """Главная функция для запуска бота."""
    try:
        logger.info("Бот запущен")
        await client.start()
        await client.run_until_disconnected()
    except Exception as e:
        logger.error(f"Ошибка при запуске бота: {e}")

# Запуск клиента
client.loop.run_until_complete(main())