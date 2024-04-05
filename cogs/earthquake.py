import discord
import requests
from discord.ext import tasks, commands
from discord import app_commands
from typing import Optional
from dotenv import load_dotenv
load_dotenv()
import os
from datetime import datetime
import sqlite3

class Earthquake(commands.GroupCog):
    def __init__(self,bot: commands.Bot):
        self.bot = bot
        self.apikey = os.getenv('WEATHERAPI')
        self.url = "https://opendata.cwa.gov.tw/api/v1/rest/datastore/E-A0015-001"
        self.params = {"Authorization":self.apikey,"limit":"1"}
        self.number = 0
    
    @app_commands.command(name="query",description="查詢近期地震警示")
    @app_commands.describe(回傳資料筆數="最大可請求數量為10")
    async def query(self,interaction: discord.Interaction,回傳資料筆數: Optional[int]):
        
        await interaction.response.defer()
        params = self.params
        
        if 回傳資料筆數 and 回傳資料筆數<=10:
            params['limit'] = 回傳資料筆數
        elif 回傳資料筆數 and 回傳資料筆數>10:
            await interaction.followup.send("資料數不得超過10")
            return 0
        else:
            回傳資料筆數 = 1
        

        data = requests.get(url=self.url,params=self.params).json()['records']["Earthquake"]
        embeds = []

       
        for i in range(len(data)):
            image = data[i]["ReportImageURI"]
            url = data[i]["Web"]
            info = data[i]["EarthquakeInfo"]

            dateandtime = datetime.fromisoformat(info["OriginTime"])
            date = dateandtime.strftime("%Y/%m/%d")
            time = dateandtime.strftime("%X")
            depth = info["FocalDepth"]
            location = info["Epicenter"]["Location"]
            magnitude = info["EarthquakeMagnitude"]["MagnitudeValue"]
            
            if data[i]["ReportColor"] == "綠色":
                color = discord.Color.green()
            elif info["ReportColor"] == "黃色":
                color = discord.Color.yellow()
            elif info["ReportColor"] == "橘色":
                color = discord.Color.orange()
            else:
                color = discord.Color.red()
            
            embed = discord.Embed(
                title="**地震報告**",
                color=color,
                description=url
                )
                    
            embed.add_field(name="時間",value=f"{date}\n{time}",inline=True)
            embed.add_field(name="震央",value=location,inline=False)
            embed.add_field(name="震源深度",value=f"{depth}公里",inline=True)
            embed.add_field(name="芮氏規模",value=magnitude,inline=True)
            embed.set_image(url=image)
            embed.timestamp = dateandtime

            embeds.append(embed)
        
            await interaction.followup.send(embeds=embeds)

async def setup(bot):
    await bot.add_cog(Earthquake(bot))