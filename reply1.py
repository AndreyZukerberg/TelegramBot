from telethon import TelegramClient, events

# Конфигурация
api_id = 20382465
api_hash = 'a83e9c7539fd0f8294b7b3b02796c90a'
source_channel = 'brytalDonetsk'
target_channel = 'ShestDonetsk'

# Создание клиента
client = TelegramClient('bot', api_id, api_hash)
print("Скрипт запущен")


@client.on(events.NewMessage(chats=source_channel))
async def my_event_handler(event):
    if event.message:
        # Пропускаем, если это часть альбома
        if event.message.grouped_id:
            return

        # Текст с добавкой
        original_text = event.message.text or ''
        final_text = f"{original_text}\n\n@ShestDonetsk"

        if event.message.media:
            await client.send_message(target_channel, final_text, file=event.message.media)
        else:
            await client.send_message(target_channel, final_text)


# Обработка альбомов (несколько медиа)
@client.on(events.Album(chats=source_channel))
async def album_handler(event):
    # Получаем общий текст для альбома
    try:
        caption = event.original_update.message.message
    except:
        caption = ""

    final_caption = f"{caption}\n\n@ShestDonetsk"

    await client.send_message(
        target_channel,
        file=event.messages,
        message=final_caption,
    )


# Запускаем клиента
client.start()
client.run_until_disconnected()