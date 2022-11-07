# bot.py
import discord
import os
from dotenv import load_dotenv
from discord.ext import commands
import asyncio


load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

intents = discord.Intents.default()
intents.members = True
intents.messages = True
intents.message_content = True


class Client(commands.Bot):
    def __init__(self):
        super().__init__(
            command_prefix=commands.when_mentioned_or("!"),
            intents=discord.Intents.all(),
            help_command=commands.DefaultHelpCommand(dm_help=True)
        )

    async def setup_hook(self): #overwriting a handler
        print(f"Logged in as   xx {client.user}")
        #await client.tree.sync()


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