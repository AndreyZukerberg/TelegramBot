from telethon import TelegramClient, events

Укажите свои API_ID, API_HASH и номер телефона

API_ID = "your_api_id" API_HASH = "your_api_hash" PHONE_NUMBER = "your_phone_number"

Словарь соответствий каналов

CHANNEL_MAPPING = { "source_channel_x": "target_channel_a", "source_channel_y": "target_channel_b", "source_channel_z": "target_channel_c", "source_channel_w": "target_channel_d", "source_channel_m": "target_channel_e", }

Создаем клиент Telethon

client = TelegramClient("forward_bot", API_ID, API_HASH)

@client.on(events.NewMessage(chats=list(CHANNEL_MAPPING.keys()))) async def forward_message(event): source_channel = event.chat.username  # Получаем юзернейм канала источника target_channel = CHANNEL_MAPPING.get(source_channel)  # Определяем целевой канал

if target_channel:
    # Пересылаем сообщение с сохранением всех вложений
    await client.send_message(target_channel, event.message)
    print(f"Переслано сообщение из {source_channel} в {target_channel}")

Запускаем бота

print("Бот запущен...") client.start(phone=PHONE_NUMBER) client.run_until_disconnected()

