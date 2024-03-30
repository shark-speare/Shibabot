import discord
from discord import app_commands
from discord.ext import commands
from discord.ext.commands import GroupCog
import sqlite3
from typing import Optional
from discord.app_commands import Choice
import os
import random

class food(GroupCog):
    def __init__(self,bot: commands.Bot):
        self.bot = bot

    @app_commands.command(name="breakfast",description="由40份早餐種類中隨機選擇")
    @app_commands.choices(種類=[
        Choice(name="中式",value="e"),
        Choice(name="西式",value="w")
    ])
    async def breakfast(self,interaction: discord.Interaction, 種類: Optional[str]):
        await interaction.response.defer()
        
        current = os.path.dirname(__file__)
        db_path = os.path.join(current,"..","database","breakfast.db")

        con = sqlite3.connect(db_path)
        cur = con.cursor()
        if 種類:
            
            cur.execute("SELECT name, des FROM breakfast WHERE region = ?",(種類,))
            result = cur.fetchall()
            final = random.choice(result)

            cur.close()
            con.close()
        
            embed = discord.Embed(
                title=final[0],
                description=final[1],
                color=discord.Colour.yellow()
            )
            region = {'w':'西式','e':'中式'}
            embed.set_footer(text=f"{region[種類]}早餐")

            await interaction.followup.send(embed=embed)
        
        
        else:
            
            try:
                cur.execute("SELECT name, des, region FROM breakfast")
                result = cur.fetchall()
                final = random.choice(result)

                cur.close()
                con.close()
            except Exception as e:
                print(e)
            embed = discord.Embed(
                title=final[0],
                description=final[1],
                color=discord.Colour.yellow()
            )
            region = {'w':'西式','e':'中式'}
            embed.set_footer(text=f"{region[final[2]]}早餐")
            
            await interaction.followup.send(embed=embed)


async def setup(bot:commands.Bot):
    await bot.add_cog(food(bot))
