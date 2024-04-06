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
from discord.app_commands import Choice

class Earthquake(commands.GroupCog):
    def __init__(self,bot: commands.Bot):
        self.bot = bot
        self.apikey = os.getenv('WEATHERAPI')
        self.allurl = "https://opendata.cwa.gov.tw/api/v1/rest/datastore/E-A0015-001"
        self.localurl = "https://opendata.cwa.gov.tw/api/v1/rest/datastore/E-A0016-001"
        self.params = {"Authorization":self.apikey,"limit":"1"}
        self.allnumber = 0
        self.localnumber = 0

    #傳入資料字典製作嵌入物件
    async def make_embed(self,dataset:dict) -> discord.Embed:
        image = dataset["ReportImageURI"]
        url = dataset["Web"]
        info = dataset["EarthquakeInfo"]

        dateandtime = datetime.fromisoformat(info["OriginTime"])
        date = dateandtime.strftime("%Y/%m/%d")
        time = dateandtime.strftime("%X")
        depth = info["FocalDepth"]
        location = info["Epicenter"]["Location"]
        magnitude = info["EarthquakeMagnitude"]["MagnitudeValue"]
        
        if dataset["ReportColor"] == "綠色":
            color = discord.Color.green()
        elif info["ReportColor"] == "黃色":
            color = discord.Color.yellow()
        elif info["ReportColor"] == "橘色":
            color = discord.Color.orange()
        else:
            color = discord.Color.red()
        
        embed = discord.Embed(
            title="",
            color=color,
            description=url
            )
                
        embed.add_field(name="時間",value=f"{date}\n{time}",inline=True)
        embed.add_field(name="震央",value=location,inline=False)
        embed.add_field(name="震源深度",value=f"{depth}公里",inline=True)
        embed.add_field(name="芮氏規模",value=magnitude,inline=True)
        embed.set_image(url=image)
        return embed

    #所有抓取
    async def fetch(self,area:str,limit:int,latest:int)-> list|discord.Embed|str : 
        params= self.params
        params['limit'] = str(limit)
        
        #顯著有感
        if area == "all":
            url = self.allurl
            data = requests.get(url=url,params=params).json()['records']["Earthquake"]
            embeds = []
            if latest == 1 and data[0]['EarthquakeNo'] == self.allnumber:
                return None
            else:
                self.allnumber = data[0]['EarthquakeNo']
           
            for i in range(len(data)):
                embed = await self.make_embed(data[i])
                embed.title = "顯著有感地震報告"
                embeds.append(embed)

            if limit > 1:
                return embeds
            else:
                return embed
        
        #區域有感
        elif area == "local":
            url = self.localurl
            data = requests.get(url=url,params=params).json()['records']["Earthquake"][0]
            if latest == 1 and data['EarthquakeNo'] == self.localnumber:
                return None
            else:
                self.localnumber = data['EarthquakeNo']
            
            embed = await self.make_embed(data)
            embed.title = "區域有感地震報告"
            return embed
            
    #開始重複
    @commands.GroupCog.listener()
    async def on_ready(self):
        self.auto.start()
    
    #手動請求
    @app_commands.command(name="query",description="查詢近期顯著有感地震報告")
    @app_commands.describe(回傳資料筆數="最大可請求數量為10")
    async def query(self,interaction: discord.Interaction,回傳資料筆數: Optional[int]):
        
        await interaction.response.defer()
        params = self.params
        
        #確保傳入限制的數字大小正確
        if 回傳資料筆數 and 1<=回傳資料筆數<=10:
            params['limit'] = 回傳資料筆數
        elif 回傳資料筆數 and 回傳資料筆數>10:
            await interaction.followup.send("資料數不得>10或<1")
            return 0
        else:
            回傳資料筆數 = 1
        

        embeds = await self.fetch("all",回傳資料筆數,0)
        
        await interaction.followup.send(embeds=embeds)
        
    #自動傳送所有地震報告 
    @tasks.loop(seconds=30)
    async def auto(self):
        
        current = os.path.dirname(__file__)
        path = os.path.join(current,"..","database","earthquake.db")
        con = sqlite3.connect(path)
        cur = con.cursor()

        embed1 = await self.fetch('all',1,1)
        if isinstance(embed1,discord.Embed):
            cur.execute("SELECT id FROM channel WHERE enable = 1")
            channels = cur.fetchall()
            

            print(channels)
            
            for id in channels:
                channel = self.bot.get_channel(id[0])
                await channel.send(embed=embed1)
        
        embed2 = await self.fetch('local',1,1)
        if isinstance(embed2,discord.Embed):
            cur.execute("SELECT id FROM channel WHERE enable = 1")
            channels = cur.fetchall()
            cur.close()
            con.close()

            for id in channels:
                channel = self.bot.get_channel(id[0])
                await channel.send(embed=embed2)

        cur.close()
        con.close()

            

async def setup(bot):
    await bot.add_cog(Earthquake(bot))