import discord
from discord.ext import commands
import feedparser
import asyncio

class News(commands.Cog):
    def __init__(self,bot):
        self.bot = bot
        self.task = bot.loop.create_task(self.news_loop())
        self.last_news = None

    async def news_loop(self):
        d = feedparser.parse("https://news.ltn.com.tw/rss/all.xml")
        self.latest_news = d.entries[0]

        if self.latest_news != self.last_news:
            self.last_news = self.latest_news
            await self.bot.get_channel(1191256045335621763).send(f"最新消息: {self.latest_news.title}")

        await asyncio.sleep(60)
        

    
async def setup(bot):
    await bot.add_cog(News(bot))