import discord
from discord.ext import commands
import requests
from classes import Ext
import json
import os
from dotenv import load_dotenv
load_dotenv

class Weather(Ext):
    def __init__(self, bot):
        self.apikey = os.getenv('WEATHERAPI')
        self.params={"Authorization":self.apikey,"format":"JSON"}

    @commands.group()
    async def weather(self,ctx):
        pass
    
    @weather.command()
    async def world(self,ctx,location):
        
        # 引入資料集
        url = "https://opendata.cwa.gov.tw/fileapi/v1/opendataapi/F-C0032-007"
        data = requests.get(url=url, params=self.params).json()["cwaopendata"]["dataset"]["location"]

        # 尋找位置
        for datas in data:
            if location == datas["locationName"]:
                index = data.index(datas)
                break
        
        # 將dataset設為該地區的資料
        dataset = data[index]["weatherElement"]

        d1, d2, d3 = {},{},{}

        # 將三天的資料分別寫入三個紀錄辭典內
        # 第一個[0]為天氣資料，第二個[0]為天
        # 由於wx的資料結構不同，所以用if else分開處理
        for eindex,ele in enumerate(["wx","tmax","tmin"],start=0):
            for dindex,day in enumerate([d1,d2,d3]):

                if ele == "wx":
                    day[ele] = dataset[eindex]["time"][dindex]["elementValue"][0]["value"]
                else:
                    day[ele] = dataset[eindex]["time"][dindex]["elementValue"]["value"]

        # 發送資料
        await ctx.send(f"{location}三日天氣預報")
        for day, des in zip([d1,d2,d3],["明天","後天","大後天"]):
            await ctx.send(f"{des}:\n天氣為{day['wx']}，溫度{day['tmin']}°C - {day['tmax']}°C")

    @weather.command(description="全台縣市近3小時天氣預報")
    async def local(self,ctx,location:str,hour:int=0):

        # 基本資料
        url = "https://opendata.cwa.gov.tw/api/v1/rest/datastore/F-D0047-089"
        params = self.params
        params["locationName"] = location
        
        if hour <= 96:
            index = hour // 3
            # 取得資料集
            dataset = requests.get(url=url, params=params).json()["records"]["locations"][0]["location"][0]["weatherElement"][6]["time"]

            value = dataset[index]["elementValue"][0]["value"]

            await ctx.send(f"{location}近{3*index}~{3*(index+1)}小時預報:\n{value}")

        else:
            await ctx.send("最多提供96小時的資料，資料序需小於32")

async def setup(bot):
    await bot.add_cog(Weather(bot))