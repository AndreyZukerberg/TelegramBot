from telethon import TelegramClient, events

# Укажите свои API_ID, API_HASH и номер телефона
API_ID = "20382465"
API_HASH = "a83e9c7539fd0f8294b7b3b02796c90a"
PHONE_NUMBER = "+380713626583"

# Словарь, где ключи - целевые каналы, а значения - списки каналов источников
CHANNEL_MAPPING = {
    "ShestDonetsk": ["chp_donetska", "itsdonetsk", "expltgk"],
}

# Создаем клиент Telethon
client = TelegramClient("forward_bot", API_ID, API_HASH)


@client.on(events.NewMessage(chats=[channel for channels in CHANNEL_MAPPING.values() for channel in channels]))
async def forward_message(event):
    source_channel = event.chat.username  # Получаем юзернейм канала источника

    # Ищем целевой канал для этого источника
    for target_channel, source_channels in CHANNEL_MAPPING.items():
        if source_channel in source_channels:
            # Если в сообщении есть медиафайлы, пересылаем их
            if event.message.media:
                # Отправляем все медиафайлы из сообщения, как одно сообщение с несколькими вложениями
                await client.send_media(target_channel, event.message.media)
            else:
                # Если медиа нет, пересылаем сообщение как текст
                await client.send_message(target_channel, event.message)

            print(f"Переслано сообщение из {source_channel} в {target_channel}")
            break  # После нахождения соответствующего канала источника выходим из цикла


# Запускаем бота
print("Бот запущен...")
client.start(phone=PHONE_NUMBER)
client.run_until_disconnected()