import discord
from discord.ext import commands
from discord import app_commands
from discord.app_commands import Choice
import requests
from dotenv import load_dotenv
import os
from typing import Optional
load_dotenv()

class Weather(commands.GroupCog):
    def __init__(self,bot:commands.Bot) -> None:
        self.bot = bot
        self.apikey = os.environ['WEATHERAPI']
        self.params={"Authorization":self.apikey,"format":"JSON"}

    @app_commands.command(name="local",description="臺灣各縣市每3小時天氣預報")
    @app_commands.choices(縣市=[
        Choice(name="臺北市",value="臺北市"),
        Choice(name="新北市",value="新北市"),
        Choice(name="桃園市",value="桃園市"),
        Choice(name="新竹縣",value="新竹縣"),
        Choice(name="苗栗縣",value="苗栗縣"),
        Choice(name="臺中市",value="臺中市"),
        Choice(name="彰化縣",value="彰化縣"),
        Choice(name="雲林縣",value="雲林縣"),
        Choice(name="嘉義縣",value="嘉義縣"),
        Choice(name="台南市",value="台南市"),
        Choice(name="高雄市",value="高雄市"),
        Choice(name="屏東縣",value="屏東縣"),
        Choice(name="臺東縣",value="臺東縣"),
        Choice(name="花蓮縣",value="花蓮縣"),
        Choice(name="宜蘭縣",value="宜蘭縣"),
        Choice(name="南投縣",value="南投縣"),
        Choice(name="澎湖縣",value="澎湖縣"),
        Choice(name="金門縣",value="金門縣"),
        Choice(name="連江縣",value="連江縣")
    ])
    @app_commands.describe(小時="起算小時，填1為0~3，填5為4~6以此類推")
    async def weather(self,interaction: discord.Interaction,縣市:Choice[str],小時:Optional[int]=0):
        
        url = "https://opendata.cwa.gov.tw/api/v1/rest/datastore/F-D0047-089"
        params = self.params
        params["locationName"] = 縣市.value
        
        if 小時 <= 96:
            index = 小時 // 3
            # 取得資料集
            dataset = requests.get(url=url, params=params).json()["records"]["locations"][0]["location"][0]["weatherElement"][6]["time"]

            value = dataset[index]["elementValue"][0]["value"]

            await interaction.response.send_message(f"{縣市.value}近{3*index}~{3*(index+1)}小時預報:\n{value}")

        else:
            await interaction.response.send_message("最多提供96小時的資料，資料序需小於32")

    @app_commands.command(name="world",description="世界各大城市三日天氣預報")
    @app_commands.describe(城市="資料由氣象局提供，沒有就是沒有")
    async def world(self,interaction: discord.Interaction,城市:str):
        
        await interaction.response.defer(ephemeral=True)

        # 引入資料集
        url = "https://opendata.cwa.gov.tw/fileapi/v1/opendataapi/F-C0032-007"
        data = requests.get(url=url, params=self.params).json()["cwaopendata"]["dataset"]["location"]

        # 尋找位置
        index = -1
        for datas in data:
            if 城市 == datas["locationName"]:
                index = data.index(datas)
                break
        
        # 將dataset設為該地區的資料

        if not index == -1:
            dataset = data[index]["weatherElement"]
        else:
            await interaction.response.send_message("查無資料，十分抱歉")
            return 0
        


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
        finallist = [f"{城市}三日天氣預報\n"]

        for day, des in zip([d1,d2,d3],["明天","後天","大後天"]): # 3 Lines
            finallist.append(f"{des}:\n天氣為{day['wx']}，溫度{day['tmin']}°C - {day['tmax']}°C\n")
        
        final = "\n".join(finallist)

        await interaction.response.send_message(final)
      

async def setup(bot):
    await bot.add_cog(Weather(bot))

