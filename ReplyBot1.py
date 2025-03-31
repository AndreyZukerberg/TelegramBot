import asyncio
import openai
from telethon import TelegramClient
from aiogram import Bot, Dispatcher
import requests

# Telegram API credentials
API_ID = "your_api_id"
API_HASH = "your_api_hash"
BOT_TOKEN = "your_bot_token"
CHAT_ID = "@your_channel"

# OpenAI API credentials
OPENAI_API_KEY = "your_openai_key"

# Sources to parse
SOURCE_CHANNELS = ["@breakingmash", "@d_code"]

client = TelegramClient("session", API_ID, API_HASH)
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(bot)

async def fetch_latest_posts(channel, limit=3):
    """Fetch latest posts from a Telegram channel."""
    async with client:
        messages = []
        async for message in client.iter_messages(channel, limit=limit):
            if message.text:
                messages.append(message.text)
        return messages

async def rewrite_news(text):
    """Use ChatGPT to shorten and enhance news with emojis."""
    response = openai.ChatCompletion.create(
        model="gpt-4-turbo",
        api_key=OPENAI_API_KEY,
        messages=[
            {"role": "user", "content": f"Сделай короткую сводку с эмодзи: {text}"}
        ]
    )
    return response["choices"][0]["message"]["content"]

async def get_image_for_news():
    """Fetch a relevant image using an AI-based search."""
    response = requests.get("https://api.unsplash.com/photos/random", params={
        "query": "news",
        "client_id": "your_unsplash_api_key"
    })
    if response.status_code == 200:
        return response.json().get("urls", {}).get("regular", "")
    return ""

async def post_news():
    """Fetch, process, and post news to Telegram."""
    for channel in SOURCE_CHANNELS:
        posts = await fetch_latest_posts(channel)
        for post in posts:
            summary = await rewrite_news(post)
            image_url = await get_image_for_news()
            message = summary
            if image_url:
                await bot.send_photo(CHAT_ID, image_url, caption=summary)
            else:
                await bot.send_message(CHAT_ID, message)
            await asyncio.sleep(10)  # Avoid spam

async def scheduler():
    """Schedule news posting 2-3 times per day."""
    while True:
        await post_news()
        await asyncio.sleep(8 * 60 * 60)  # 8 hours between posts

if __name__ == "__main__":
    asyncio.run(scheduler())