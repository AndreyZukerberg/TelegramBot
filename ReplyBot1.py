import logging
from telethon import TelegramClient, events
from telethon.tl.functions.messages import SendMediaRequest
from telethon.tl.types import InputPeerChannel, InputPeerUser
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

client = TelegramClient(phone_number, api_id, api_hash)

async def send_message(client, target_channel, text, media=None):
    """Отправка сообщения в канал с медиа."""
    if media:
        # Отправка медиа файлов, отправляем сразу все медиа в одном сообщении
        await client.send_message(target_channel, text=text, media=media)
    else:
        # Отправка только текста
        await client.send_message(target_channel, text=text)

async def handle_message(event, source_channel):
    """Обрабатывает входящие сообщения и пересылает их в целевые каналы."""
    # Получаем данные о сообщении
    message = event.message

    # Пересылка в целевой канал
    target_channel = channel_mapping.get(source_channel)
    if target_channel:
        # Пересылаем в целевой канал
        if message.media:
            # Отправка медиа в одном сообщении
            media = message.media
            await send_message(client, target_channel, message.text, media=media)
        else:
            # Отправка только текста
            await send_message(client, target_channel, message.text)

@client.on(events.NewMessage(from_users=list(channel_mapping.keys())))
async def forward_message(event):
    """Обрабатывает новые сообщения от указанных каналов источников."""
    source_channel = event.sender_id
    await handle_message(event, source_channel)

async def main():
    """Главная функция для запуска бота."""
    logging.info("Бот запущен")
    await client.start()
    await client.run_until_disconnected()

# Запуск клиента
client.loop.run_until_complete(main())