import aiohttp
from aiogram import Bot, Dispatcher, types
from aiogram.enums import ParseMode
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
import os
import sqlite3
import logging
import asyncio
import imagehash
from PIL import Image
import numpy as np
import cv2
import ffmpeg

# Токен бота
TOKEN = "7616945089:AAFBZnirPqwYdGl_ZfG-cXC31qTdwnAxqVM"

# Каналы
SOURCE_CHANNELS = ["@chp_donetska", "@itsdonetsk", "@expltgk"]  # Публичные каналы
TARGET_CHANNEL = "@ShestDonetsk"  # Публичный целевой канал
ADMIN_ID = 123456789  # ID администратора

# Настройка логирования
logging.basicConfig(level=logging.INFO)

# Инициализация бота с конфигурацией
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties

# Устанавливаем настройки для бота
properties = DefaultBotProperties(parse_mode=ParseMode.HTML)

# Теперь создаём сессию с помощью aiohttp.ClientSession
async def create_bot():
    session = aiohttp.ClientSession()
    bot = Bot(token=TOKEN, session=session, default=properties)
    return bot

# Инициализация диспетчера
async def main():
    bot = await create_bot()  # Получаем объект бота асинхронно
    dp = Dispatcher(bot)  # Передаем готовый объект бота в Dispatcher

    # Далее ваш основной код с обработчиками
    # Пример для обработки сообщений из каналов
    @dp.message_handler(content_types=types.ContentType.TEXT)
    async def handle_message(message: types.Message):
        # Ваши действия с сообщением
        pass

    # Запуск бота
    await dp.start_polling()

if __name__ == "__main__":
    asyncio.run(main())  # Запуск асинхронной функции