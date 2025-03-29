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

# Список ключевых слов для фильтрации рекламы
ad_keywords = [
    "реклама", "маркетинг", "брендинг", "целевая аудитория", "рекламные кампании", "SMM", "SEO", 
    "инфлюенсеры", "таргетинг", "баннеры", "видеоролики", "продвижение", "рекламные платформы", 
    "реклама.", "#реклама"
]

# Настройка логирования
logging.basicConfig(level=logging.INFO)

client = TelegramClient(phone_number, api_id, api_hash)

async def remove_ads(text):
    """Удаляет из текста ссылки и слова, связанные с рекламой."""
    # Убираем все ссылки и рекламные фразы
    for word in ad_keywords:
        text = re.sub(rf'\b{re.escape(word)}\b', '', text, flags=re.IGNORECASE)
    text = re.sub(r'https?://\S+', '', text)  # Удаление ссылок
    return text.strip()

async def send_message(client, target_channel, text, media=None):
    """Отправка сообщения в канал с медиа."""
    if media:
        # Отправка медиа файлов
        await client.send_message(target_channel, text=text, media=media)
    else:
        # Отправка только текста
        await client.send_message(target_channel, text=text)

async def handle_message(event, source_channel):
    """Обрабатывает входящие сообщения и пересылает их в целевые каналы."""
    # Получаем данные о сообщении
    message = event.message

    # Фильтрация рекламы
    text = message.text
    filtered_text = await remove_ads(text)

    # Если сообщение не содержит рекламы, пересылаем его в соответствующий канал
    if filtered_text != text:
        # Логируем рекламный пост
        logging.info(f"Найден рекламный пост в канале {source_channel}")
        
        # Отправляем администратору для модерации
        await client.send_message('@NoTrustNetAdmin', 'Пост требует модерации:\n' + message.text)
    else:
        # Получаем целевой канал, соответствующий источнику
        target_channel = channel_mapping.get(source_channel)
        if target_channel:
            # Пересылаем в целевой канал
            if message.media:
                # Отправка медиа
                await send_message(client, target_channel, filtered_text, media=message.media)
            else:
                # Отправка только текста
                await send_message(client, target_channel, filtered_text)

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