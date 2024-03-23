import discord
from discord.ext import commands
import os
import asyncio
import json
from dotenv import load_dotenv
load_dotenv()

bot = commands.Bot(command_prefix='>',intents = discord.Intents.all())

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}")

@bot.command()
async def load(ctx,ext):
    await bot.load_extension(f'cogs.{ext}')
    await ctx.send(f'{ext} loaded')

@bot.command()
async def reload(ctx,ext):
    await bot.reload_extension(f'cogs.{ext}')
    await ctx.send(f'{ext} reloaded')
    
    

async def loadext():
    for filename in os.listdir('./cogs'):
        if filename.endswith('.py'):
            await bot.load_extension(f'cogs.{filename[:-3]}')
            print(f"{filename[:-3]} loaded.")

async def main():
    await loadext()
    await bot.start(os.getenv('TOKEN'))

asyncio.run(main())