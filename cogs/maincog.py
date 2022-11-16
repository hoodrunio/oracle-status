from discord.ext import commands, tasks
from kujira import KujiraPool
from kujira.models import session, User as Validator
from config import *
from datetime import datetime

HELPMSG = """

**Commands**

Help
    ```!bothelp```

Register for missing price check for given operator address:
    ```!addr <validator_address> <threshold> @user1 @user2... ```
*Example:*
    ```!addr kujiravaloper1ujhlm5qxyt2hn5fxq8wll805tsxcamqfhsty9a 50 @user1 @user2 @user3 @user4```

Add additional users for notifying given operator address:
    ```!adduser <validator_address>  @user1 @user2... ```
*Example:*
    ```!adduser kujiravaloper1ujhlm5qxyt2hn5fxq8wll805tsxcamqfhsty9a @user1 @user2 @user3 @user4```

Remove users from notification list for  given operator address:
    ```!removeme  <validator_address>```
*Example:*
    ```!removeme kujiravaloper1ujhlm5qxyt2hn5fxq8wll805tsxcamqfhsty9a```

List signed up validors
    ```!validators```

List details for given operator address:
    ```!detail <validator_address```
*Example:*
    ```!detail kujiravaloper1ujhlm5qxyt2hn5fxq8wll805tsxcamqfhsty9a```

"""

pool = KujiraPool()
for node_url in SERVERS:
    pool.add_node(node_url)
pool.update_selected()


channelid = 1038491075855257612  # test
channelid = 992186951358746797   # main


class MainCog(commands.Cog):
    def __init__(self, bot, kujirapool):
        self.bot = bot
        self.pool = kujirapool

    @commands.Cog.listener()
    async def on_ready(self):
        print("ready")
        validators = session.query(Validator).all()
        for v in validators:
            print(v.moniker)
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
            
        await self.bot.process_commands(message)

    @commands.command(pass_context=True)
    async def addr(self, ctx, address, threshold, *args):
        if ctx.channel.id == channelid:
            msg = self.pool.add_validator("<@"+str(ctx.author.id)+">", address, threshold)
            validator = session.query(Validator).filter_by(address=address).first()
            for user in args:
                print("user is ", user)
                state = validator.add_notify(user)
                if state is False:
                    msg += f"\nUser name {user} is already in the list for {validator.moniker}, not adding\n"

            msg += f"Current list of users to notify for moniker {validator.moniker}:\n"
            session.refresh(validator)
            msg += validator.notify_list()
            await ctx.send(msg)

    @commands.command(pass_context=True)
    async def removeme(self, ctx, address):
        if ctx.channel.id == channelid:
            validator = session.query(Validator).filter_by(address=address).first()        
            msg = ""
            user = "<@"+str(ctx.author.id)+">"
            state = validator.delete_notify(user)
            if state:
                msg += f"User name {user} is deleted from  list for {validator.moniker}\n"
            else:
                msg += f"User name {user} NOT in the list for {validator.moniker}\n"
            session.refresh(validator)
            if len(validator.notify) > 0:
                msg += f"\n\nCurrent list of users to notify for {validator.moniker}:\n"
                msg += validator.notify_list()
            await ctx.send(msg)
        
    @commands.command(pass_context=True)
    async def adduser(self, ctx, address, *args):
        if ctx.channel.id == channelid:
            validator = session.query(Validator).filter_by(address=address).first()
            msg = ""
            for user in args:
                state = validator.add_notify(user)
                if state is False:
                    msg += f"User name {user} is already in the list for {validator.moniker}, not adding\n"
            msg += f"Current list of users to notify for {validator.moniker}:\n"
            session.refresh(validator)
            msg += validator.notify_list()
            await ctx.send(msg)

    @commands.command(pass_context=True)
    async def validators(self, ctx):
        if ctx.channel.id == channelid:
            msg = "List of validators :\n```"
            for moniker, address in self.pool.validator_list():
                msg += "  " + address + "  " + moniker + "\n"
            msg += "```"
            await ctx.send(msg)

    @commands.command(pass_context=True)
    async def detail(self, ctx, address):
        if ctx.channel.id == channelid:
            validator = session.query(Validator).filter_by(address=address).first()
            msg = f"**Moniker :** {validator.moniker}\n**Address :** {validator.address}\n**Notification list:** \n"
            msg += validator.notify_list()
            await ctx.send(msg)

    @commands.command(pass_context=True)
    async def bothelp(self, ctx):
        if ctx.channel.id == channelid:
            await ctx.send(HELPMSG, delete_after=60)

    @tasks.loop(seconds=5)
    async def check_alarms(self):
        msg = "Alarms: \n"
        alarm_state = False
        channel = self.bot.get_channel(channelid)
        validators = session.query(Validator).all()
        for validator in validators:
            state = validator.check_alarm_status()
            if state:
                alarm_state = True
                msg += validator.alarm_message()
        if alarm_state:
            await channel.send(msg)


async def setup(bot):
    await bot.add_cog(MainCog(bot, pool))
