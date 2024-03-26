import discord
import requests
from discord.ext import tasks, commands
from discord import app_commands
from typing import Optional
from dotenv import load_dotenv
load_dotenv()
import os

class Earthquake(commands.GroupCog):
    def __init__(self,bot: commands.Bot):
        self.bot = bot
        self.apikey = os.getenv('WEATHERAPI')
        self.url = "https://opendata.cwa.gov.tw/api/v1/rest/datastore/E-A0015-001"
        self.params = {"Authorization":self.apikey,"limit":"1"}
    
    @app_commands.command(name="query",description="查詢近期地震警示")
    async def query(self,interaction: discord.Interaction,):
        await interaction.response.defer()
        params = self.params
        

        data = requests.get(url=self.url,params=self.params).json()['records']["Earthquake"][0]

       
        
        
        url = data["ReportImageURI"]
        title = data["ReportContent"]

        value = data["EarthquakeInfo"]["EarthquakeMagnitude"]["MagnitudeValue"]

        if value <= 3:
            color = discord.Colour.green()
        elif value <= 5:
            color = discord.Colour.yellow()
        else:
            color = discord.Colour.red()

        embed = discord.Embed(
            title=title,
            color = color,
            )
        embed.set_image(url=url)

        await interaction.followup.send(embed=embed)
        
    

async def setup(bot):
    await bot.add_cog(Earthquake(bot))