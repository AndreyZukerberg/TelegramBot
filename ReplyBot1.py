import logging
from telethon import TelegramClient, events

# Настройки для подключения
api_id = 20382465  # Ваш API ID
api_hash = "a83e9c7539fd0f8294b7b3b02796c90a"  # Ваш API Hash
phone_number = "+380713626583"  # Ваш номер телефона

# Идентификаторы каналов
source_channel = 'expltgk'  # Канал-источник
target_channel = 'ShestDonetsk'  # Целевой канал

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Создание клиента
client = TelegramClient(phone_number, api_id, api_hash)

@client.on(events.NewMessage(from_channels=[source_channel]))
async def forward_message(event):
    """Функция для пересылки сообщения."""
    try:
        message = event.message
        # Пересылаем сообщение в целевой канал
        await client.send_message(target_channel, message)
        logger.info(f"Сообщение переслано из {source_channel} в {target_channel}")
    except Exception as e:
        logger.error(f"Ошибка при пересылке сообщения: {e}")

async def main():
    """Основная функция для запуска бота."""
    try:
        logger.info("Бот запущен")
        await client.start()
        await client.run_until_disconnected()
    except Exception as e:
        logger.error(f"Ошибка при запуске бота: {e}")

# Запуск клиента
client.loop.run_until_complete(main())