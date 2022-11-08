from discord.ext import commands, tasks
from kujira import KujiraPool
from config import *
from datetime import datetime

HELPMSG = """
Commands
!addr  validator_address threshold list of users : signup for missing block check for given validator address
     !addr kujiravaloper1ujhlm5qxyt2hn5fxq8wll805tsxcamqfhsty9a  120  user1 user2 user3 user4
!adduser 
"""

pool = KujiraPool()
for node_url in SERVERS:
    pool.add_node(node_url)
pool.update_selected()

channelid = 1038491075855257612


class MainCog(commands.Cog):
    def __init__(self, bot, pool):
        self.bot = bot
        self.pool = pool


    @commands.Cog.listener()
    async def on_ready(self):
        print("ready")
        self.check_alarms.start()

    @commands.command(pass_context=True)
    async def on_message(self, message):
        # Make sure the Bot doesn't respond to it's own messages
        if message.author == self.bot.user:
            return

        if message.content == 'hello':
            print(message.author, " said hello")
            await message.channel.send(f'Hi {message.author}')
        if message.content == 'bye':
            await message.channel.send(f'Goodbye {message.author}')
        if message.content == "help":
            await message.channel.send(HELPMSG)
            
        await self.bot.process_commands(message)

    @commands.command(pass_context=True)
    async def addr(self, ctx, address, threshold, *args):
        msg = self.pool.add_validator(ctx.author.name, address, threshold)
        validator = self.pool.validators.get_validator(address)
        for user in args:
            state = validator.add_notify(user)
            if state is False:
                msg += f"User name {user} is already in the list for {address}, not adding\n"
        msg += f"Current list of users to notify for {address}:\n"
        msg += validator.notify_list()
        await ctx.send(msg)

    @commands.command(pass_context=True)
    async def adduser(self, ctx, address, *args):
        validator = self.pool.validators.get_validator(address)
        msg = ""
        for user in args:
            state = validator.add_notify(user)
            if state is False:
                msg += f"User name {user} is already in the list for {address}, not adding\n"
        msg += f"Current list of users to notify for {address}:\n"
        msg += validator.notify_list()
        await ctx.send(msg)

    @commands.command(pass_context=True)
    async def validators(self, ctx):
        msg = "List of validators :\n"
        for vals in self.pool.validators.validators:
            msg += "  " + vals.address + "\n"
        await ctx.send(msg)

    @commands.command(pass_context=True)
    async def detail(self, ctx, address):
        validator = self.pool.validators.get_validator(address)
        msg = f"Moniker : {validator.moniker}, Address : {validator.address}\nNotification list: \n"
        msg += validator.notify_list()
        await ctx.send(msg)

    @commands.command(pass_context=True)
    async def bothelp(self, ctx):
        await ctx.send(HELPMSG)

    @tasks.loop(seconds=60)
    async def check_alarms(self):
        # check the alarm status here.
        # missing block information will be retrieved with another application via cron
        # it will populate the database, we only check with the provided numbers
        # is it ok to generate alarm for each validator.
        msg = "Alarms: \n"
        alarm_state = False
        
        channel = self.bot.get_channel(channelid)
        for validator in self.pool.validators.validators:
            state = validator.check_alarm_status()
            if state:
                alarm_state = True
                # raise alarm
                msg += validator.alarm_message()
        if alarm_state:
            await channel.send(msg)



async def setup(bot):
    await bot.add_cog(MainCog(bot, pool))
