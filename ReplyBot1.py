import logging
import os
from aiogram import Bot, Dispatcher, types
from aiogram.types import ParseMode
from aiogram.utils import executor
import google.generativeai as genai
from dotenv import load_dotenv

# Загружаем ключ API из .env
load_dotenv()
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

# Настройка Google Gemini
genai.configure(api_key=GOOGLE_API_KEY)

# Токен бота
API_TOKEN = "your_telegram_bot_token_here"
bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)

# Админ для управления ботом
ADMIN_ID = 123456789  # Замени на свой ID

# Устанавливаем уровень логирования
logging.basicConfig(level=logging.INFO)

async def improve_text_with_gemini(text: str) -> str:
    try:
        response = genai.generate_text(prompt=text)
        return response.text.strip()
    except Exception as e:
        logging.error(f"Ошибка при обращении к Google Gemini: {e}")
        return text

@dp.message_handler(commands=['start'])
async def cmd_start(message: types.Message):
    if message.from_user.id == ADMIN_ID:
        await message.answer("Бот активирован. Перешли пост для обработки.")
    else:
        await message.answer("Извините, только для администратора.")

@dp.message_handler(content_types=[types.ContentType.TEXT, types.ContentType.PHOTO, types.ContentType.VIDEO])
async def handle_post(message: types.Message):
    if message.from_user.id != ADMIN_ID:
        return

    # Обработка текста
    original_text = message.text or ""
    improved_text = await improve_text_with_gemini(original_text)

    # Создаем кнопки
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    button_forward = types.KeyboardButton("Переслать")
    button_skip = types.KeyboardButton("Не пересылать")
    keyboard.add(button_forward, button_skip)

    # Ответ на сообщение
    if message.content_type == 'text':
        await message.answer(f"Улучшенный текст:\n\n{improved_text}", reply_markup=keyboard)
    else:
        # Если есть медиа
        media = message.photo[-1] if message.photo else message.video
        if media:
            await message.answer_media_group(media=[media])
        await message.answer(f"Улучшенный текст:\n\n{improved_text}", reply_markup=keyboard)

@dp.message_handler(lambda message: message.text == "Переслать")
async def forward_post(message: types.Message):
    if message.from_user.id != ADMIN_ID:
        return

    # Отправляем улучшенный пост в канал
    await bot.send_message(chat_id="@NoTrustNet", text=message.text)
    await message.answer("Пост отправлен в канал!")

@dp.message_handler(lambda message: message.text == "Не переслать")
async def skip_post(message: types.Message):
    if message.from_user.id != ADMIN_ID:
        return

    await message.answer("Пост не был отправлен.")

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)