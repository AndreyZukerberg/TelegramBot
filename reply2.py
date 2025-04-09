from telethon import TelegramClient, events
import re

# Конфигурация
api_id = 20382465
api_hash = 'a83e9c7539fd0f8294b7b3b02796c90a'
source_channel = 'chp_donetska'
target_channel = 'Donetsk24na7'

# Создание клиента
client = TelegramClient('bot1', api_id, api_hash)
print("Скрипт запущен")

# Бан-ворды и фильтры
ban_words = [
    "Мы находимся",
    "Наши каналы:",
    "Не упустите шанс",
]

def clean_text(text: str) -> str:
    if not text:
        return "@Donetsk24na7"

    # Удаляем строки, содержащие "Написать нам" и "Подписаться на канал"
    text = re.sub(r".*Написать нам.*(\n)?", "", text, flags=re.IGNORECASE)
    text = re.sub(r".*Подписаться на канал.*(\n)?", "", text, flags=re.IGNORECASE)

    # Удаляем Markdown-ссылки: [текст](https://t.me/...)
    text = re.sub(r"\[.*?\]\(https?://t\.me/.*?\)", "", text)

    # Удаляем просто голые ссылки на Telegram
    text = re.sub(r"https?://t\.me/\S+", "", text)

    # Удаляем лишние пробелы, пустые строки
    text = re.sub(r"\n\s*\n", "\n", text)
    text = text.strip()

    return f"{text}\n\n@Donetsk24na7"

def contains_advertising(text: str) -> bool:
    if not text:
        return False
    text_lower = text.lower()

    # Бан-ворды
    if any(ban_word.lower() in text_lower for ban_word in ban_words):
        return True

    # Номера телефонов, начинающиеся на +7949
    if re.search(r"\+7949\d{6,}", text_lower):
        return True

    return False



@client.on(events.NewMessage(chats=source_channel))
async def my_event_handler(event):
    if event.message:
        # Пропускаем, если это часть альбома
        if event.message.grouped_id:
            return

        original_text = event.message.text or ''
        if contains_advertising(original_text):
            print("⛔ Пост содержит рекламу — пропущен.")
            return

        final_text = clean_text(original_text)

        if event.message.media:
            await client.send_message(target_channel, final_text, file=event.message.media)
        else:
            await client.send_message(target_channel, final_text)


@client.on(events.Album(chats=source_channel))
async def album_handler(event):
    try:
        caption = event.original_update.message.message or ''
    except:
        caption = ''

    if contains_advertising(caption):
        print("⛔ Альбом содержит рекламу — пропущен.")
        return

    final_caption = clean_text(caption)

    await client.send_message(
        target_channel,
        file=event.messages,
        message=final_caption,
    )

# Запускаем клиента
client.start()
client.run_until_disconnected()
