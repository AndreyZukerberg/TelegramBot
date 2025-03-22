import asyncio
import logging
from aiogram import Bot, Dispatcher, types
from aiogram.types import ParseMode, ContentType
from aiogram.utils import executor
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
import re
from io import BytesIO
from PIL import Image
import cv2
import numpy as np
import hashlib

# Включение логирования
logging.basicConfig(level=logging.INFO)

# Токен бота
TOKEN = 'your_bot_token'
ADMIN_ID = 123456789  # ID администратора для модерации

# Каналы-источники и целевой канал
SOURCE_CHANNELS = ['@chp_donetska', '@itsdonetsk', '@expltgk']
TARGET_CHANNEL = '@ShestDonetsk'

# Создание бота и диспетчера
bot = Bot(token=TOKEN)
dp = Dispatcher(bot)

# Словарь для хранения хешей обработанных сообщений (для дубликатов)
processed_hashes = set()

# Функция для проверки на рекламу
def is_advertisement(text):
    ad_keywords = ['реклама', 'скидка', 'купить', 'распродажа']
    return any(keyword in text.lower() for keyword in ad_keywords)

# Функция для удаления водяных знаков с изображений
def remove_watermark(image):
    # Пример обработки изображения (простая операция, зависит от водяного знака)
    np_image = np.array(image)
    gray = cv2.cvtColor(np_image, cv2.COLOR_BGR2GRAY)
    _, thresh = cv2.threshold(gray, 240, 255, cv2.THRESH_BINARY)
    result = cv2.inpaint(np_image, thresh, 3, cv2.INPAINT_TELEA)
    return Image.fromarray(result)

# Функция для обработки текста и удаления нежелательных фраз
def clean_text(text):
    unwanted_phrases = ['нежелательная фраза']  # Добавь сюда фразы для удаления
    for phrase in unwanted_phrases:
        text = text.replace(phrase, '')
    text += "\n\nПодписывайтесь на @ShestDonetsk!"
    return text

# Проверка на дубликаты
def is_duplicate(message):
    msg_hash = hashlib.md5(message.encode('utf-8')).hexdigest()
    if msg_hash in processed_hashes:
        return True
    processed_hashes.add(msg_hash)
    return False

# Функция для отправки сообщения админу для модерации
async def send_to_admin_for_moderation(message):
    keyboard = InlineKeyboardMarkup()
    keyboard.add(InlineKeyboardButton("Отправить", callback_data=f"send:{message.message_id}"))
    keyboard.add(InlineKeyboardButton("Удалить", callback_data=f"delete:{message.message_id}"))
    await bot.send_message(ADMIN_ID, f"Потенциальная реклама:\n\n{message.text}", reply_markup=keyboard)

# Функция для пересылки поста в целевой канал
async def forward_to_target_channel(message):
    text = clean_text(message.text)
    if message.photo:
        photo = await bot.get_file(message.photo[-1].file_id)
        photo_bytes = await bot.download_file(photo.file_path)
        image = Image.open(BytesIO(photo_bytes))
        image = remove_watermark(image)
        with BytesIO() as byte_io:
            image.save(byte_io, format="PNG")
            byte_io.seek(0)
            await bot.send_photo(TARGET_CHANNEL, byte_io, caption=text)
    else:
        await bot.send_message(TARGET_CHANNEL, text, parse_mode=ParseMode.HTML)

# Хендлер для новых сообщений
@dp.message_handler(content_types=[ContentType.TEXT, ContentType.PHOTO])
async def handle_new_post(message: types.Message):
    if message.chat.username in SOURCE_CHANNELS:
        if is_advertisement(message.text):
            await send_to_admin_for_moderation(message)
        elif is_duplicate(message.text):
            logging.info(f"Дубликат сообщения: {message.text}")
        else:
            await forward_to_target_channel(message)

# Хендлер для обработки команд администратора
@dp.callback_query_handler(lambda c: c.data.startswith("send"))
async def process_send(callback_query: types.CallbackQuery):
    message_id = callback_query.data.split(":")[1]
    message = await bot.get_message(callback_query.message.chat.id, message_id)
    await forward_to_target_channel(message)
    await callback_query.answer("Сообщение отправлено!")

@dp.callback_query_handler(lambda c: c.data.startswith("delete"))
async def process_delete(callback_query: types.CallbackQuery):
    message_id = callback_query.data.split(":")[1]
    await bot.delete_message(callback_query.message.chat.id, message_id)
    await callback_query.answer("Сообщение удалено!")

# Главная асинхронная функция
async def on_start():
    logging.info("Бот запущен и работает!")
    await dp.start_polling()

# Запуск бота
if __name__ == '__main__':
    asyncio.run(on_start())