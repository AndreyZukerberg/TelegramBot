import os
import asyncio
import sqlite3
import logging
import imagehash
from PIL import Image
import numpy as np
import cv2
import ffmpeg
from aiogram import Bot, Dispatcher, types
from aiogram.client.bot import DefaultBotProperties
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram import F

# Токен бота
TOKEN = "7616945089:AAFBZnirPqwYdGl_ZfG-cXC31qTdwnAxqVM"

# Каналы
SOURCE_CHANNELS = ["-1001234567890", "-1009876543210"]  # ID каналов
TARGET_CHANNEL = "-1001122334455"  # ID целевого канала
ADMIN_ID = 123456789  # ID администратора

# Настройка логирования
logging.basicConfig(level=logging.INFO)

# Создание объекта DefaultBotProperties
default_properties = DefaultBotProperties(parse_mode="HTML")

# Инициализация бота с использованием default_properties
bot = Bot(token=TOKEN, default=default_properties)

dp = Dispatcher()

# База данных для хранения хешей сообщений
conn = sqlite3.connect("bot_data.db")
cur = conn.cursor()
cur.execute("""
    CREATE TABLE IF NOT EXISTS posts (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        text_hash TEXT,
        image_hash TEXT,
        video_hash TEXT
    )
""")
conn.commit()

# Фильтр рекламы
AD_WORDS = ["реклама", "подпишись", "скидка", "акция", "купить", "магазин", "партнерство"]

def is_advertisement(text):
    """Проверка, является ли текст рекламным."""
    text = text.lower()
    return any(word in text for word in AD_WORDS)

def get_text_hash(text):
    """Получение хеша текста."""
    return str(imagehash.phash(Image.fromarray(np.array(bytearray(text.encode()), dtype=np.uint8).reshape(1, -1))))

def get_image_hash(image_path):
    """Получение хеша изображения."""
    image = Image.open(image_path).convert("L").resize((8, 8))
    return str(imagehash.phash(image))

def get_video_hash(video_path):
    """Получение хеша первого кадра видео."""
    cap = cv2.VideoCapture(video_path)
    success, frame = cap.read()
    cap.release()
    if success:
        image = Image.fromarray(frame).convert("L").resize((8, 8))
        return str(imagehash.phash(image))
    return None

def remove_watermark(image_path):
    """Простое удаление вотермарок."""
    image = cv2.imread(image_path)
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    _, mask = cv2.threshold(gray, 240, 255, cv2.THRESH_BINARY)
    image[mask == 255] = (255, 255, 255)
    output_path = image_path.replace(".jpg", "_clean.jpg")
    cv2.imwrite(output_path, image)
    return output_path

def clean_text(text):
    """Удаление рекламных фраз и добавление ссылки."""
    to_remove = ["💬Написать нам", "Подписаться на канал✅", "Подписаться | Предложить новость"]
    for phrase in to_remove:
        text = text.replace(phrase, "")
    text += f"\n\n🔗 <a href='https://t.me/ShestDonetsk'>Подписаться</a>"
    return text.strip()

@dp.message(F.chat.id.in_(SOURCE_CHANNELS))  # Фильтрация по ID каналов
async def handle_channel_post(message: types.Message):
    """Обработка новых сообщений в канале."""
    if message.text and is_advertisement(message.text):
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="✅ Отправить", callback_data=f"approve_{message.message_id}")],
            [InlineKeyboardButton(text="❌ Удалить", callback_data=f"reject_{message.message_id}")]
        ])
        await bot.send_message(ADMIN_ID, f"⚠️ ВОЗМОЖНАЯ РЕКЛАМА ⚠️\n\n{message.text}", reply_markup=keyboard)
        return

    text_hash = get_text_hash(message.text) if message.text else None
    image_hash = None
    video_hash = None

    # Проверка дубликатов
    cur.execute("SELECT id FROM posts WHERE text_hash = ? OR image_hash = ? OR video_hash = ?", (text_hash, image_hash, video_hash))
    if cur.fetchone():
        return

    # Обработка изображений
    if message.photo:
        photo = message.photo[-1]
        file = await bot.get_file(photo.file_id)
        file_path = f"downloads/{photo.file_id}.jpg"
        await bot.download_file(file.file_path, file_path)
        image_hash = get_image_hash(file_path)

        # Удаление вотермарки
        clean_path = remove_watermark(file_path)
        await bot.send_photo(TARGET_CHANNEL, photo=open(clean_path, "rb"), caption=clean_text(message.caption or ""))

    # Обработка видео
    elif message.video:
        file = await bot.get_file(message.video.file_id)
        file_path = f"downloads/{message.video.file_id}.mp4"
        await bot.download_file(file.file_path, file_path)
        video_hash = get_video_hash(file_path)

        # Удаление вотермарки (заглушка)
        await bot.send_video(TARGET_CHANNEL, video=open(file_path, "rb"), caption=clean_text(message.caption or ""))

    # Сохранение хешей
    cur.execute("INSERT INTO posts (text_hash, image_hash, video_hash) VALUES (?, ?, ?)", (text_hash, image_hash, video_hash))
    conn.commit()

    # Пересылка текста
    if message.text:
        await bot.send_message(TARGET_CHANNEL, clean_text(message.text))

@dp.callback_query(F.data)
async def moderation_callback(callback_query: types.CallbackQuery):
    """Обработка модерации постов."""
    action, msg_id = callback_query.data.split("_")

    if action == "approve":
        msg = await bot.forward_message(TARGET_CHANNEL, ADMIN_ID, int(msg_id))
        await callback_query.message.edit_text(f"✅ Отправлено в канал {TARGET_CHANNEL}")

    elif action == "reject":
        await callback_query.message.edit_text("❌ Пост удален")

    await callback_query.answer()

async def main():
    """Запуск бота."""
    os.makedirs("downloads", exist_ok=True)
    await bot.delete_webhook(drop_pending_updates=True)

    # Регистрация обработчиков
    dp.message(lambda message: message.chat.id in SOURCE_CHANNELS)(handle_channel_post)

    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())