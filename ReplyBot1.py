import re
import asyncio
from aiogram import Bot, Dispatcher, F, types
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.types import Message, FSInputFile, InlineKeyboardButton, InlineKeyboardMarkup, InputMediaPhoto, InputMediaVideo
from aiogram.filters import CommandStart
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.client.session.aiohttp import AiohttpSession

# Токен бота и настройки
BOT_TOKEN = "7820665212:AAE0E7QmLEc7VkNboc-h27YDMiWqWXl_kes"
ADMIN_ID = 7324661214  # Telegram ID @NoTrustNetAdmin
TARGET_CHANNEL = "@NoTrustNet"

default_properties = DefaultBotProperties(parse_mode=ParseMode.HTML)

bot = Bot(token=BOT_TOKEN, session=AiohttpSession(), default=default_properties)
dp = Dispatcher()

# Удаление webhook перед запуском
async def remove_webhook():
    try:
        await bot.delete_webhook()
        print("Webhook успешно удален")
    except Exception as e:
        print(f"Ошибка при удалении webhook: {e}")

# Удаление ссылок
def clean_text(text: str) -> str:
    text = re.sub(r'\[.*?\]\(.*?\)', '', text)  # Markdown ссылки
    text = re.sub(r'<a\s+href=".*?">.*?</a>', '', text)  # HTML ссылки
    text = re.sub(r'https?://\S+', '', text)
    text = re.sub(r'www\.\S+', '', text)
    text = re.sub(r't\.me/\S+', '', text)
    text = re.sub(r'\s+', ' ', text).strip()
    return f"{text}\n\n@NoTrustNet"

# Храним посты в памяти
posts_storage = {}

# Кнопки
def get_keyboard(post_id):
    kb = InlineKeyboardBuilder()
    kb.button(text="Переслать пост", callback_data=f"send:{post_id}")
    kb.button(text="Не отправлять", callback_data=f"cancel:{post_id}")
    return kb.as_markup()

@dp.message(F.from_user.id == ADMIN_ID)
async def handle_post(message: Message):
    media_group = []
    text = message.caption or message.text or ""

    if not message.media_group_id:
        post_id = str(message.message_id)
        clean = clean_text(text)

        if message.photo:
            posts_storage[post_id] = {"media": message.photo[-1].file_id, "text": clean, "type": "photo"}
            await bot.send_photo(chat_id=ADMIN_ID, photo=message.photo[-1].file_id, caption=clean, reply_markup=get_keyboard(post_id))
        elif message.video:
            posts_storage[post_id] = {"media": message.video.file_id, "text": clean, "type": "video"}
            await bot.send_video(chat_id=ADMIN_ID, video=message.video.file_id, caption=clean, reply_markup=get_keyboard(post_id))
        elif message.document:
            posts_storage[post_id] = {"media": message.document.file_id, "text": clean, "type": "document"}
            await bot.send_document(chat_id=ADMIN_ID, document=message.document.file_id, caption=clean, reply_markup=get_keyboard(post_id))
        elif text:
            posts_storage[post_id] = {"media": None, "text": clean, "type": "text"}
            await bot.send_message(chat_id=ADMIN_ID, text=clean, reply_markup=get_keyboard(post_id))

    # Если группа медиа (альбом)
    else:
        group_id = message.media_group_id
        if group_id not in posts_storage:
            posts_storage[group_id] = {"media": [], "text": text}

        if message.photo:
            posts_storage[group_id]["media"].append(InputMediaPhoto(media=message.photo[-1].file_id))
        elif message.video:
            posts_storage[group_id]["media"].append(InputMediaVideo(media=message.video.file_id))

        # Если это последний пост в альбоме — ждем 1 секунду и отправляем
        await asyncio.sleep(1)
        if len(posts_storage[group_id]["media"]) >= 2:
            clean = clean_text(posts_storage[group_id]["text"])
            posts_storage[group_id]["media"][0].caption = clean
            await bot.send_media_group(chat_id=ADMIN_ID, media=posts_storage[group_id]["media"])
            await bot.send_message(chat_id=ADMIN_ID, text="Выберите действие:", reply_markup=get_keyboard(group_id))

@dp.callback_query(F.data.startswith("send:"))
async def send_post(call: types.CallbackQuery):
    post_id = call.data.split(":")[1]
    post = posts_storage.get(post_id)

    if not post:
        await call.message.edit_text("Пост не найден или устарел.")
        return

    if post.get("media") and post.get("type") == "photo":
        await bot.send_photo(chat_id=TARGET_CHANNEL, photo=post["media"], caption=post["text"])
    elif post.get("media") and post.get("type") == "video":
        await bot.send_video(chat_id=TARGET_CHANNEL, video=post["media"], caption=post["text"])
    elif post.get("media") and post.get("type") == "document":
        await bot.send_document(chat_id=TARGET_CHANNEL, document=post["media"], caption=post["text"])
    elif post.get("type") == "text":
        await bot.send_message(chat_id=TARGET_CHANNEL, text=post["text"])
    elif isinstance(post.get("media"), list):
        post["media"][0].caption = clean_text(post["text"])
        await bot.send_media_group(chat_id=TARGET_CHANNEL, media=post["media"])

    await call.message.edit_text("Пост отправлен.")

@dp.callback_query(F.data.startswith("cancel:"))
async def cancel_post(call: types.CallbackQuery):
    await call.message.edit_text("Пост отменён.")

# Запуск
async def main():
    # Удаляем webhook перед запуском
    await remove_webhook()
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
