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
!addr  validator_address threshold list of users : signup for missing block check for given validator address
     !addr kujiravaloper1ujhlm5qxyt2hn5fxq8wll805tsxcamqfhsty9a  120  user1 user2 user3 user4
!adduser 
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
async def save_address(ctx, address, threshold, *args):
    msg = pool.add_validator(ctx.author.name, address, threshold)
    validator = pool.validators.get_validator(address)
    for user in args:
        state = validator.add_notify(user)
        if state is False:
            msg += f"User name {user} is already in the list for {address}, not adding\n"
    msg += f"Current list of users to notify for {address}:\n"
    msg += validator.notify_list()
    await ctx.send(msg)


@bot.command(name="adduser")
async def add_notify_user(ctx, address, *args):
    validator = pool.validators.get_validator(address)
    msg = ""
    for user in args:
        state = validator.add_notify(user)
        if state is False:
            msg += f"User name {user} is already in the list for {address}, not adding\n"
    msg += f"Current list of users to notify for {address}:\n"
    msg += validator.notify_list()
    await ctx.send(msg)


@bot.command(name="detail")
async def save_address(ctx, address):
    validator = pool.validators.get_validator(address)
    msg = f"Moniker : {validator.moniker}, Address : {validator.address}\nNotification list: \n"
    msg += validator.notify_list()
    await ctx.send(msg)


@bot.command(name="bothelp")
async def save_address(ctx):
    await ctx.send(HELPMSG)


bot.run(TOKEN)
