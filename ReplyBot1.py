import logging import asyncio from telethon import TelegramClient, events, Button

Настройки бота

API_ID = "your_api_id" API_HASH = "your_api_hash" PHONE_NUMBER = "your_phone_number"  # Добавленная строка с номером телефона

Каналы источники и назначения

CHANNELS_MAP = { "chp_donetska": "ShestDonetsk", "moscowach": "MosNevSlp", "mash_siberia": "ShestNovosib", "e1_news": "ShestEKB", "kazancity": "ShestKazan", "incidentkld": "ShestKaliningrad", "etorostov": "ShestRostov", "moynizhny": "ShestNN", "naebnet": "NoTrustNet", "expltgk": ["ShestDonetsk", "MosNevSlp", "ShestNovosib", "ShestEKB", "ShestKazan", "ShestKaliningrad", "ShestRostov", "ShestNN", "NoTrustNet"] }

Админ для модерации

ADMIN_USERNAME = "NoTrustNetAdmin"

Ключевые слова для фильтрации рекламы

AD_KEYWORDS = {"реклама", "маркетинг", "брендинг", "SMM", "SEO", "инфлюенсеры", "таргетинг", "рекламные кампании"}

Логирование

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s") logger = logging.getLogger(name)

Создание клиента

client = TelegramClient("bot_session", API_ID, API_HASH)

@client.on(events.NewMessage(chats=list(CHANNELS_MAP.keys()))) async def forward_message(event): source_channel = event.chat.username or event.chat.id target_channels = CHANNELS_MAP.get(source_channel, []) if not isinstance(target_channels, list): target_channels = [target_channels]

# Проверка на рекламу
if any(word.lower() in event.raw_text.lower() for word in AD_KEYWORDS):
    await send_to_admin(event)
    return

# Пересылка в целевые каналы
for target in target_channels:
    try:
        await client.send_message(target, event.message)
    except Exception as e:
        logger.error(f"Ошибка при пересылке сообщения в {target}: {e}")

async def send_to_admin(event): buttons = [ [Button.inline("Отправить", b"send"), Button.inline("Отклонить", b"reject")] ] await client.send_message(ADMIN_USERNAME, event.message, buttons=buttons)

@client.on(events.CallbackQuery()) async def callback_handler(event): if event.sender.username != ADMIN_USERNAME: return

if event.data == b"send":
    source_channel = event.message.chat.username or event.message.chat.id
    target_channels = CHANNELS_MAP.get(source_channel, [])
    if not isinstance(target_channels, list):
        target_channels = [target_channels]
    
    for target in target_channels:
        try:
            await client.send_message(target, event.message)
        except Exception as e:
            logger.error(f"Ошибка при пересылке подтвержденного сообщения в {target}: {e}")
    await event.answer("Сообщение отправлено")
elif event.data == b"reject":
    await event.answer("Сообщение отклонено")

async def main(): await client.start(phone=PHONE_NUMBER) logger.info("Бот запущен") await client.run_until_disconnected()

if name == "main": asyncio.run(main())

