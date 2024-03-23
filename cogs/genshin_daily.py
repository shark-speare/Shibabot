import discord
from discord.ext import commands, tasks
import genshin


class Daily(commands.Cog):

    def __init__(self, bot):
        self.cookies = {
            "ltuid": "305640397",
            "ltoken": "f2I0qsMRGZGmPXH1bwTIplJh9fgJ4ic0cAYdogqG"
        }
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        self.genshin_daily.start()

    @tasks.loop(hours=24)
    async def genshin_daily(self):
        client = genshin.Client(cookies=self.cookies,
                                lang="zh-tw",
                                game=genshin.Game.GENSHIN)

        channel = self.bot.get_channel(1198545752436248586)

        try:
            reward = await client.claim_daily_reward()
        except genshin.AlreadyClaimed:
            await channel.send(f"今天已經領取過了")
        else:
            await channel.send(f"今天領取了{reward.amount}個{reward.name}")


async def setup(bot):
    await bot.add_cog(Daily(bot))
