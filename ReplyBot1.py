import os
import shutil
import logging
from telethon import TelegramClient, events
from telethon.tl.types import InputMediaPhoto

# Настройка логирования
logging.basicConfig(level=logging.INFO)

# Укажите свои данные
api_id = 20382465
api_hash = "a83e9c7539fd0f8294b7b3b02796c90a"
phone_number = "+380713626583"

# Создание клиента
client = TelegramClient('shest_bot', api_id, api_hash)

# Каналы
source_channel = 'expltgk'
target_channel = 'ShestDonetsk'

# Функция для скачивания фото
async def download_media(message):
    media_files = []
    download_folder = "./downloads/"
    os.makedirs(download_folder, exist_ok=True)

    if message.media:
        file_path = await client.download_media(message.media, download_folder)
        if file_path:
            logging.info(f"Скачан файл: {file_path}")
            media_files.append(file_path)

    return media_files


# Функция загрузки и отправки медиа
async def send_message_with_media(message, media_files):
    try:
        # Загружаем файлы на сервер Telegram
        uploaded_files = []
        for file in media_files:
            uploaded_file = await client.upload_file(file)
            if uploaded_file:
                uploaded_files.append(uploaded_file)

        # Если есть несколько файлов, отправляем их группой
        if len(uploaded_files) > 1:
            await client.send_file(target_channel, uploaded_files)
            logging.info(f"Группа медиа отправлена в {target_channel}")
        elif len(uploaded_files) == 1:
            # Если только один файл, отправляем его как одиночное медиа
            await client.send_file(target_channel, uploaded_files[0])
            logging.info(f"Одиночный медиа файл отправлен в {target_channel}")

        # Отправка текста
        if message.text:
            await client.send_message(target_channel, message.text)
            logging.info("Текст сообщения отправлен.")

        # Удаление файлов и папки
        for file in media_files:
            if os.path.exists(file):
                os.remove(file)
        shutil.rmtree("./downloads/")

    except Exception as e:
        logging.error(f"Ошибка при отправке: {str(e)}")


# Обработчик новых сообщений
@client.on(events.NewMessage(chats=source_channel))
async def handler(event):
    message = event.message
    logging.info(f"Получено сообщение {message.id}")

    media_files = await download_media(message)
    await send_message_with_media(message, media_files)


# Запуск бота
async def main():
    await client.start(phone_number)
    logging.info("Бот запущен.")
    await client.run_until_disconnected()


if __name__ == "__main__":
    client.loop.run_until_complete(main())
