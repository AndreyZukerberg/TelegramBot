import asyncio
import aiohttp
from bs4 import BeautifulSoup
from aiogram import Bot, Dispatcher
from aiogram.types import InputMediaPhoto, InputMedia

API_TOKEN = "YOUR_TELEGRAM_BOT_TOKEN"
MODERATOR_ID = "@Brofflovski"

bot = Bot(token=API_TOKEN)
dp = Dispatcher()

news_sources = {
    "rbc": "https://rssexport.rbc.ru/rbcnews/news/tech/",
    "ria": "https://ria.ru/export/rss2/archive/index.xml",
    "kodru": "https://kod.ru/feed/"
}

async def fetch_news(url):
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            if response.status != 200:
                return []
            content = await response.text()
    
    soup = BeautifulSoup(content, "xml")
    items = soup.find_all("item")[:5]
    news_list = []
    
    for item in items:
        title = item.title.text
        link = item.link.text
        image_url = item.enclosure["url"] if item.find("enclosure") else None
        news_list.append({"title": title, "link": link, "image": image_url})
    
    return news_list

async def send_news():
    for source, url in news_sources.items():
        news_list = await fetch_news(url)
        for news in news_list:
            text = f"{news['title']}\n\n🔗 [Читать полностью]({news['link']})"
            if news["image"]:
                media = [InputMediaPhoto(news["image"], caption=text, parse_mode="Markdown")]
                await bot.send_media_group(chat_id=MODERATOR_ID, media=media)
            else:
                await bot.send_message(chat_id=MODERATOR_ID, text=text, parse_mode="Markdown")

async def main():
    while True:
        await send_news()
        await asyncio.sleep(10800)  # Раз в 3 часа

if __name__ == "__main__":
    asyncio.run(main())