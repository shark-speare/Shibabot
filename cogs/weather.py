import discord
from discord.ext import commands
from discord import app_commands
from discord.app_commands import Choice
import requests
from dotenv import load_dotenv
import os
from typing import Optional
from datetime import datetime as d
load_dotenv()

class Weather(commands.GroupCog):
    def __init__(self,bot:commands.Bot) -> None:
        self.bot = bot
        self.apikey = os.environ['WEATHERAPI']
        self.params={"Authorization":self.apikey,"format":"JSON"}

    @app_commands.command(name="local",description="臺灣各縣市每3小時天氣預報")
    @app_commands.choices(縣市=[
        Choice(name="臺北市",value="0"),
        Choice(name="新北市",value="1"),
        Choice(name="桃園市",value="2"),
        Choice(name="新竹縣",value="3"),
        Choice(name="臺南市",value="4"),
        Choice(name="高雄市",value="5"),
        Choice(name="基隆市",value="6"),
        Choice(name="新竹縣",value="7"),
        Choice(name="新竹市",value="8"),
        Choice(name="苗栗縣",value="9"),
        Choice(name="彰化縣",value="10"),
        Choice(name="南投縣",value="11"),
        Choice(name="雲林縣",value="12"),
        Choice(name="嘉義縣",value="13"),
        Choice(name="嘉義市",value="14"),
        Choice(name="屏東縣",value="15"),
        Choice(name="宜蘭縣",value="16"),
        Choice(name="花蓮縣",value="17"),
        Choice(name="臺東縣",value="18"),
        Choice(name="澎湖縣",value="19"),
        Choice(name="金門縣",value="20"),
        Choice(name="連江縣",value="21"),
    ])
    async def weather(self,interaction: discord.Interaction,縣市:Choice[str]):
        await interaction.response.defer()

        url = "https://opendata.cwa.gov.tw/fileapi/v1/opendataapi/F-C0032-005"
        params = self.params
        locationindex = int(縣市.value)
        
        #取得資料與建立嵌入物件
        data = requests.get(url=url,params=params).json()['cwaopendata']['dataset']['location'][locationindex]['weatherElement']
        embed = discord.Embed(title=f"{縣市.name}未來一周天氣預報",color=discord.Colour.blue())
        

        #數字與日期對應表
        week = {
            0:"一",
            1:"二",
            2:"三",
            3:"四",
            4:"五",
            5:"六",
            6:"日",
        }

        #加入嵌入區塊
        for i in range(0,13,2):

            date = d.fromisoformat(data[0]['time'][i]['startTime'])
            date = date.strftime(f"%m/%d({week[date.weekday()]})")
            
            wx = data[0]['time'][i]['parameter']['parameterName']
            wxvalue = int(data[0]['time'][i]['parameter']['parameterValue'])
            maxt = data[1]['time'][i]['parameter']['parameterName']
            mint = data[2]['time'][i]['parameter']['parameterName']

            if wxvalue == 1:
               weatheremoji = ":sunny:"
            elif 2 <= wxvalue <= 3:
               weatheremoji = ":white_sun_small_cloud:"
            elif 4 <= wxvalue <= 7:
               weatheremoji = ":white_sun_cloud:"
            elif 8 <= wxvalue <= 10:
               weatheremoji = ":white_sun_rain_cloud:"
            else:
               weatheremoji = ":cloud_rain:"

            # if int(maxt) <= 10:
            #     tempemoji = ":snowflake:"
            # elif int(maxt) <= 25:
            #     tempemoji = ":wind_chime:"
            # else:
            #     tempemoji = ":thermometer:"

    
            embed.add_field(name=date,value=f"{weatheremoji}{wx}\n{mint}-{maxt}°C")

        try:
            await interaction.followup.send(embed = embed)
        except Exception as e:
            await interaction.followup.send(str(e))

    @app_commands.command(name="world",description="世界各大城市三日天氣預報")
    @app_commands.describe(城市="資料由氣象局提供，沒有就是沒有")
    async def world(self,interaction: discord.Interaction,城市:str):
        
        await interaction.response.defer(ephemeral=False)

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
            await interaction.followup.send("查無資料，十分抱歉")
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

        await interaction.followup.send(final)
      

async def setup(bot):
    await bot.add_cog(Weather(bot))

