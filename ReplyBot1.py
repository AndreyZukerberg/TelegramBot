import logging
import re
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackQueryHandler
from telegram.ext import CallbackContext

# Включаем логирование для отладки
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)
logger = logging.getLogger(__name__)

# Указания на каналы и бота
SOURCE_CHANNEL = '@naebnet'  # Канал-источник
TARGET_CHANNEL = '@NoTrustNet'  # Канал-цель
ADMIN_CHAT_ID = '@NoTtustNetadm'  # Админ канал для проверки
BOT_TOKEN = '7820665212:AAE0E7QmLEc7VkNboc-h27YDMiWqWXl_kes'  # Токен бота

# Регулярное выражение для определения рекламных постов
AD_REGEX = re.compile(r"(Реклама|ООО\s\"[^\"]+\".*ИНН\s\d{10,12})", re.IGNORECASE)


# Функция фильтрации рекламных сообщений
def is_advertisement(text: str) -> bool:
    # Проверяем наличие слов, указывающих на рекламу
    if 'Реклама' in text or 'ООО' in text or 'ИНН' in text:
        return bool(AD_REGEX.search(text))
    return False


# Функция обработки новых сообщений
async def forward_message(update: Update, context: CallbackContext) -> None:
    message = update.message

    # Проверяем, является ли сообщение рекламой
    if is_advertisement(message.text):
        # Отправляем сообщение админу для проверки
        keyboard = [
            [InlineKeyboardButton("Отправить", callback_data='approve'),
             InlineKeyboardButton("Запретить", callback_data='deny')]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await context.bot.send_message(
            ADMIN_CHAT_ID,
            text=f"Новый пост на проверку:\n\n{message.text}",
            reply_markup=reply_markup,
            disable_notification=True
        )
    else:
        # Пересылаем сообщение в целевой канал
        await context.bot.send_message(
            TARGET_CHANNEL,
            text=message.text,
            parse_mode="HTML",
            disable_web_page_preview=True
        )


# Обработка выбора админа
async def button(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    await query.answer()

    if query.data == 'approve':
        # Если админ выбрал "Отправить", пересылаем сообщение в канал
        message_id = context.user_data.get('message_id')
        if message_id:
            await context.bot.forward_message(
                TARGET_CHANNEL,
                query.message.chat.id,
                message_id
            )
        await query.edit_message_text(text="Пост отправлен в канал.")

    elif query.data == 'deny':
        # Если админ выбрал "Запретить", ничего не отправляем
        await query.edit_message_text(text="Пост отклонён.")


# Основная функция для запуска бота
def main() -> None:
    application = Application.builder().token(BOT_TOKEN).build()

    # Регистрируем обработчики
    application.add_handler(MessageHandler(filters.Chat(SOURCE_CHANNEL) & filters.TEXT, forward_message))
    application.add_handler(CallbackQueryHandler(button))

    # Запуск бота
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == '__main__':
    main()
