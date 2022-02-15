import discord # import discord.py
from discord.ext import commands # import additional discord.py functionality
#import random # RNG
#import typing # allow parameters to be optional
import os # import the OS details, including our hidden bot token
import asyncpg # import async/await postgres
# import asyncio

db = None

## Connecting the DB ----------------------------------------------------------
async def run():
    global db
    
    dbURL = os.environ.get('DATABASE_URL')
    db = await asyncpg.connect(dsn=dbURL, ssl='require')
    
## Bot Setup ----------------------------------------------------------
    
token = os.environ.get('DISCORD_BOT_TOKEN') # This is hosted on HEROKU

client = discord.Client()

intents = discord.Intents.default()
intents.members = True

bot = commands.Bot(command_prefix="prefix!", intents=intents, db=db)

## Code Here ----------------------------------------------------------


## Bot Setup & Activation ----------------------------------------------------------
asyncio.get_event_loop().run_until_complete(run())
bot.run(token)
