import logging
import asyncio
import google.generativeai as genai
from aiogram import Bot, Dispatcher, types, F
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, Message
from aiogram.filters import Command
import re

# 🔐 Ваши ключи
BOT_TOKEN = "7820665212:AAE0E7QmLEc7VkNboc-h27YDMiWqWXl_kes"
GOOGLE_API_KEY = "AIzaSyA8AQxfsbH0Un8ejnShzfQ0FnaQfDXlJMI"
ADMIN_ID = 7324661214
CHANNEL_ID = "@NoTrustNet"

# Настройка Google Gemini API
genai.configure(api_key=GOOGLE_API_KEY)

# Создаем бота и диспетчер
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# Настроим логирование
logging.basicConfig(level=logging.INFO)

MAX_CAPTION_LENGTH = 1024  # Максимальная длина подписи


# Промт для генерации текста с помощью Google Gemini
def generate_prompt(text: str) -> str:
    return f"""
    Ты — AI-редактор новостей. Твоя задача — переписать новость в лаконичном и информативном стиле, как в канале @naebnet.

Требования:

    Новость должна быть краткой.

    Добавь выделения нужного текста.

    Сохрани нейтральный и слегка ироничный тон, текст должен быть официальным.

    Если новость техническая, объясни её простыми словами.

    Убери лишнюю информацию и воду, оставь только суть.

    Перепиши заголовок так, чтобы он привлекал внимание, заголовок нужно выделять болдом и ентером после заголовка.

Пример входных данных:
«Черный четверг для инвесторов: рынки рушатся, США вводят новые пошлины, капитализация американского рынка падает на $1,7 трлн. Apple переживает худший день за 5 лет: акции -8%, капитализация -$300 млрд. Бигтех в минусе: Nvidia -5%, Qualcomm -7%, Amazon -9%. Под ударом и российский рынок: индекс Мосбиржи ниже 2900, сильнее всего страдают Газпром, Роснефть и Сургутнефтегаз.»

Пример желаемого результата:
«Черный четверг для инвесторов: фондовые рынки по всему миру падают на фоне новых пошлин США. Капитализация американского рынка обвалилась (https://www.bloomberg.com/news/articles/2025-04-03/trump-tariffs-set-to-zap-nearly-2-trillion-from-us-stock-market) на $1,7 трлн сразу после открытия торгов.

У Apple сегодня худший день за последние 5 лет. Акции компании в минусе на 8%, а капитализация — на $300 млрд. Падает весь бигтех: Nvidia (-5%), Qualcomm (-7%), Amazon (-9%).

Затронуло и российский рынок. Индекс Мосбиржи упал ниже 2900 пунктов. Сильнее всего пострадали Газпром, Роснефть и Сургутнефтегаз.»

Теперь обработай следующую новость:
{text}
    """


async def improve_text_with_gemini(text: str) -> str:
    """Обрабатывает текст с помощью Google Gemini и форматирует его."""
    try:
        # Генерация текста с использованием промта
        prompt = generate_prompt(text)

        model = genai.GenerativeModel("models/gemini-1.5-pro-latest")  # Используем доступную модель
        response = model.generate_content([prompt])  # Генерация текста
        improved_text = response.text.strip() if hasattr(response, 'text') else text

        # Убираем ссылки
        improved_text = re.sub(r'http\S+', '', improved_text)  # Удаляем ссылки

        return improved_text
    except Exception as e:
        logging.error(f"Ошибка при работе с Google Gemini: {e}")
        return text  # Возвращаем оригинальный текст в случае ошибки


@dp.message(Command("start"))
async def cmd_start(message: Message):
    """Стартовое сообщение"""
    if message.from_user.id == ADMIN_ID:
        await message.answer("✅ Бот активирован. Перешли пост для обработки.")
    else:
        await message.answer("⛔ Этот бот доступен только для администратора.")


@dp.message(F.forward_from_chat | F.text | F.photo | F.video)
async def handle_post(message: Message):
    """Обрабатывает пересланный пост (с медиа или без)"""
    if message.from_user.id != ADMIN_ID:
        return

    # Получаем текст поста
    original_text = message.caption or message.text or "Нет текста"
    improved_text = await improve_text_with_gemini(original_text)

    # Если текст слишком длинный, обрезаем до 1024 символов
    if len(improved_text) > MAX_CAPTION_LENGTH:
        improved_text = improved_text[:MAX_CAPTION_LENGTH - 3] + "..."  # Добавляем многоточие, чтобы не превысить лимит

    # Создаем клавиатуру с кнопками
    buttons = [
        [InlineKeyboardButton(text="✅ Переслать", callback_data="send_post")],
        [InlineKeyboardButton(text="❌ Не пересылать", callback_data="cancel_post")]
    ]
    keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)

    # Если в посте есть медиа
    if message.photo:
        await message.answer_photo(photo=message.photo[-1].file_id,
                                   caption=improved_text, reply_markup=keyboard)
    elif message.video:
        await message.answer_video(video=message.video.file_id, caption=improved_text,
                                   reply_markup=keyboard)
    else:
        await message.answer(improved_text, reply_markup=keyboard)


@dp.callback_query(F.data == "send_post")
async def send_post(callback: types.CallbackQuery):
    """Пересылает пост в канал"""
    if callback.from_user.id != ADMIN_ID:
        return

    # Проверяем, что текст не пустой
    text_to_send = callback.message.text
    if text_to_send is None or not text_to_send.strip():  # Проверка на None
        await callback.message.edit_text("❌ Текст пустой. Пост не был отправлен.")
        await callback.answer()
        return

    # Пересылаем текст в канал
    await bot.send_message(chat_id=CHANNEL_ID, text=text_to_send)
    await callback.message.edit_text("✅ Пост отправлен в канал!")
    await callback.answer()


@dp.callback_query(F.data == "cancel_post")
async def cancel_post(callback: types.CallbackQuery):
    """Отменяет отправку поста"""
    if callback.from_user.id != ADMIN_ID:
        return

    await callback.message.edit_text("❌ Пост не был отправлен.")
    await callback.answer()


async def main():
    """Запускает бота"""
    logging.info("🤖 Бот запущен!")
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
