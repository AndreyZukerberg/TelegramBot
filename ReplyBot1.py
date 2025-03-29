from telethon import TelegramClient, events, Button
import logging

# Логирование
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("TelegramForwarder")

# Настройки
API_ID = "YOUR_API_ID"
API_HASH = "YOUR_API_HASH"
BOT_TOKEN = "YOUR_BOT_TOKEN"

ADMIN_ID = "NoTrustNetAdmin"

# Каналы источники и назначения
CHANNELS = {
    "chp_donetska": "ShestDonetsk",
    "moscowach": "MosNevSlp",
    "mash_siberia": "ShestNovosib",
    "e1_news": "ShestEKB",
    "kazancity": "ShestKazan",
    "incidentkld": "ShestKaliningrad",
    "etorostov": "ShestRostov",
    "moynizhny": "ShestNN",
    "naebnet": "NoTrustNet",
    "expltgk": [
        "ShestDonetsk", "MosNevSlp", "ShestNovosib", "ShestEKB", "ShestKazan",
        "ShestKaliningrad", "ShestRostov", "ShestNN", "NoTrustNet"
    ],
    "https://t.me/+QUo4lv3MKq04Yjk6": "Piterburg24na7"
}

# Ключевые слова для фильтрации рекламы
AD_KEYWORDS = [
    "реклама", "маркетинг", "брендинг", "SMM", "SEO", "лендинги", "инфлюенсеры",
    "ретаргетинг", "рекламные кампании", "контекстная реклама", "социальные сети"
]

# Создание бота
client = TelegramClient("bot", API_ID, API_HASH).start(bot_token=BOT_TOKEN)

# Обработчик сообщений
@client.on(events.NewMessage(chats=list(CHANNELS.keys())))
async def forward_message(event):
    source_chat = event.chat_id
    target_chats = CHANNELS.get(event.chat.username, [])
    if not isinstance(target_chats, list):
        target_chats = [target_chats]

    # Проверка на рекламу
    if any(keyword in event.raw_text.lower() for keyword in AD_KEYWORDS):
        await client.send_message(ADMIN_ID, "🚨 Найдена реклама! Что делать?", buttons=[
            [Button.inline("Отправить", data=f"approve:{event.id}"), Button.inline("Отклонить", data=f"reject:{event.id}")]
        ])
        return

    # Пересылка в каналы назначения
    for chat in target_chats:
        try:
            await client.send_message(chat, event.message)
        except Exception as e:
            logger.error(f"Ошибка при отправке сообщения в {chat}: {e}")

# Обработчик кнопок модерации
@client.on(events.CallbackQuery())
async def callback_handler(event):
    data = event.data.decode("utf-8")
    action, msg_id = data.split(":")
    message = await event.get_message()

    if action == "approve":
        for chat in CHANNELS.values():
            if isinstance(chat, list):
                for sub_chat in chat:
                    await client.send_message(sub_chat, message)
            else:
                await client.send_message(chat, message)
        await event.edit("✅ Сообщение отправлено!")
    elif action == "reject":
        await event.edit("🚫 Сообщение отклонено!")

# Запуск бота
logger.info("Бот запущен")
client.run_until_disconnected()
