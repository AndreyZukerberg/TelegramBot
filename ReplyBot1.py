from telethon import TelegramClient, events

# Укажите свои API_ID, API_HASH и номер телефона
API_ID = "your_api_id"
API_HASH = "your_api_hash"
PHONE_NUMBER = "your_phone_number"

# Словарь, где ключи - целевые каналы, а значения - списки каналов источников
CHANNEL_MAPPING = {
    "target_channel_a": ["source_channel_x", "source_channel_y", "source_channel_z"],
    "target_channel_b": ["source_channel_w", "source_channel_m"],
    "target_channel_c": ["source_channel_n", "source_channel_o"],
}

# Создаем клиент Telethon
client = TelegramClient("forward_bot", API_ID, API_HASH)

@client.on(events.NewMessage(chats=[channel for channels in CHANNEL_MAPPING.values() for channel in channels]))
async def forward_message(event):
    source_channel = event.chat.username  # Получаем юзернейм канала источника
    
    # Ищем целевой канал для этого источника
    for target_channel, source_channels in CHANNEL_MAPPING.items():
        if source_channel in source_channels:
            # Пересылаем сообщение с сохранением всех вложений
            await client.send_message(target_channel, event.message)
            print(f"Переслано сообщение из {source_channel} в {target_channel}")
            break  # После нахождения соответствующего канала источника выходим из цикла

# Запускаем бота
print("Бот запущен...")
client.start(phone=PHONE_NUMBER)
client.run_until_disconnected()