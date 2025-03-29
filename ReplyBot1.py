from telethon import TelegramClient, events
from telethon.tl.types import InputMediaPhoto, InputMediaVideo, InputMediaDocument

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
            # Если в сообщении есть несколько медиафайлов, отправляем их все
            media_files = []
            if event.message.media:
                # Проверяем, если в сообщении несколько медиафайлов
                if hasattr(event.message, 'media') and event.message.media:
                    # Если это несколько фото/видео
                    if isinstance(event.message.media, InputMediaPhoto):
                        media_files.append(InputMediaPhoto(event.message.media))
                    elif isinstance(event.message.media, InputMediaVideo):
                        media_files.append(InputMediaVideo(event.message.media))
                    elif isinstance(event.message.media, InputMediaDocument):
                        media_files.append(InputMediaDocument(event.message.media))

                if len(media_files) > 1:
                    await client.send_media(target_channel, media_files)
                else:
                    await client.send_message(target_channel, event.message)
            else:
                # Если медиа нет, пересылаем сообщение как текст
                await client.send_message(target_channel, event.message)

            print(f"Переслано сообщение из {source_channel} в {target_channel}")
            break  # После нахождения соответствующего канала источника выходим из цикла


# Запускаем бота
print("Бот запущен...")
client.start(phone=PHONE_NUMBER)
client.run_until_disconnected()