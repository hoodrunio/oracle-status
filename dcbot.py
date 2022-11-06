# bot.py
import discord
import os
from dotenv import load_dotenv
from kujira import KujiraPool
from config import *

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

from discord.ext import commands

pool = KujiraPool()
for node_url in SERVERS:
    pool.add_node(node_url)
pool.update_selected()

intents = discord.Intents.default()
intents.members = True
intents.messages = True
intents.message_content = True


bot = commands.Bot(command_prefix="!", intents=intents)

HELPMSG = """
Commands
!addr  validator_address threshold : signup for missing block check for given validator address
"""


@bot.event
async def on_ready():
    print(f'{bot.user} succesfully logged in!')


@bot.event
async def on_message(message):
    # Make sure the Bot doesn't respond to it's own messages
    if message.author == bot.user:
        return

    if message.content == 'hello':
        print(message.author, " said hello")
        await message.channel.send(f'Hi {message.author}')
    if message.content == 'bye':
        await message.channel.send(f'Goodbye {message.author}')

    await bot.process_commands(message)


@bot.command(name="addr")
async def save_address(ctx, address, threshold):
    msg = pool.add_validator(ctx.author.name, address, threshold)
    await ctx.send(msg)


@bot.command(name="bothelp")
async def save_address(ctx):
    await ctx.send(HELPMSG)


bot.run(TOKEN)
