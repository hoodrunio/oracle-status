# bot.py
import discord
import os
from dotenv import load_dotenv
from discord.ext import commands
import asyncio


DEPLOY="main" # or DEPLOY="test"

TOKEN = ""
ENGINE= ""

load_dotenv()
if DEPLOY == "main":
    TOKEN = os.getenv('DISCORD_TOKEN_MAIN')
    ENGINE = os.getenv('DISCORD_ENGINE_MAIN')
    
elif DEPLOY == "test":
    TOKEN = os.getenv('DISCORD_TOKEN_TEST')
    ENGINE = os.getenv('DISCORD_ENGINE_TEST')


class Client(commands.Bot):
    def __init__(self):
        super().__init__(
            command_prefix=commands.when_mentioned_or("!"),
            intents=discord.Intents.all(),
            help_command=commands.DefaultHelpCommand(dm_help=True)
        )


    async def setup_hook(self): #overwriting a handler
        print(f"Logged in as {client.user}")

async def load_extensions():
    await client.load_extension("cogs.maincog")

client = Client()

async def main():
    async with client:
        await load_extensions()
        await client.start(TOKEN)

asyncio.run(main())
"""
bot = commands.Bot(command_prefix="!", intents=intents)
load_extension()
bot.run(TOKEN)

"""
