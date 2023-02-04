import asyncio
import json
import os
import random
import time
from typing import Union

import discord
from discord import TextChannel, VoiceChannel, StageChannel, ForumChannel, app_commands, Intents, Client, Interaction
from discord.ext import commands

import resources
from resources import load_data, check_admin


# class Bot(discord.Client):
#     def __init__(self, *, intents: Intents):
#         super().__init__(intents=intents)
#         self.tree = discord.app_commands.CommandTree(self)
#
#     async def setup_hook(self) -> None:
#         await self.tree.sync()
#
#
# client = Bot(intents=var.intentsOutput)
bot = commands.Bot(command_prefix=var.determine_prefix, intents=var.intents)
bot.remove_command("help")
bot.remove_command("editchannel")
embed = discord.Embed


class Events(commands.Cog):
    def __init__(self, Bot: commands.Bot):
        self.bot = Bot

    @commands.Cog.listener()
    async def on_member_join(self, member: discord.Member):
        await member.create_dm()
        await member.dm_channel.send(embed=discord.Embed(title=f"Welcome to"
                                                               f" {member.guild.name}!",
                                                         description=f"Hi {member.mention}!"
                                                                     f" Welcome to {member.guild.name},"
                                                                     f" owned by {member.guild.owner.name}",
                                                         color=var.color))
        data = load_data()
        data[str(member.guild.id)]["members"].append({"name": member.name, "id": member.id, "cash": 0})
        with open("guild.json", "w") as j:
            json.dump(data, j)

    @commands.Cog.listener()
    async def on_guild_join(self, guild: discord.Guild):
        for member in guild.members:
            if member.guild_permissions.administrator:
                await member.create_dm()
                await member.dm_channel.send(f"Hi!:sweat_smile:")
        data = load_data()
        if not str(guild.id) in data:
            membersListGuild = []
            for l in guild.members:
                membersListGuild.append({"name": l.name, "id": l.id, "cash": 0})
            data.update({str(guild.id): {"members": membersListGuild,
                                         "prefixes": var.defaultPrefix,
                                         "rules": var.defaultRules}})
            with open("guild.json", "w") as j:
                json.dump(data, j)


class Cash(commands.Cog):
    def __init__(self, Bot: commands.Bot):
        self.bot = Bot

    @commands.command(name="mycash")
    async def ctx_cash(self, ctx: commands.Context):
        """Sends the amount of cash the user has."""
        currentCash = None
        for memberData in load_data([str(ctx.guild.id), "members"]):
            if memberData.get("id") == ctx.message.author.id:
                currentCash = memberData.get("cash")
        if currentCash is None:
            await ctx.send(f"{ctx.author.display_name.capitalize()} don't have any cash")
        else:
            await ctx.send(f"{ctx.author.display_name.capitalize()} cash is {currentCash}")

    @commands.command(name="getcash")
    async def user_cash(self, ctx: commands.Context, user: discord.User = None):
        """Sends the user's cash."""
        # check args
        if user is None:
            await ctx.send(f"Please specify a user.")
            return None
        # define vars
        currentCash = None
        # get user's cash
        for memberData in load_data([str(ctx.guild.id), "members"]):
            if memberData.get("id") == user.id:
                currentCash = memberData.get("cash")
                break
        # checks if data exist
        if currentCash is None:
            await ctx.send(f"{user.display_name.capitalize()} don't have any cash")
        else:
            await ctx.send(f"{user.display_name.capitalize()} cash is {currentCash}")

    @commands.command(name="setcash")
    async def set_cash(self, ctx: commands.Context, user: discord.User = None, amount: int = None):
        """Set the user's cash."""
        if await check_admin(ctx):
            if user is None:
                await ctx.send(f"Please specify a user.")
                return None
            if amount is None:
                await ctx.send(f"Please specify amount.")
                return None
            membersData = load_data([str(ctx.guild.id), "members"])
            for memberIndex in range(len(membersData)):
                if membersData[memberIndex].get("id") == user.id:
                    data = load_data()
                    data.get(str(ctx.guild.id)).get("members")[memberIndex]["cash"] = amount
                    await ctx.send(f'{user.display_name.capitalize()} cash is now {amount}')
                    with open(r"./guild.json", "w") as i:
                        json.dump(data, i)
                    break


class Moderation(commands.Cog):
    def __init__(self, Bot: commands.Bot):
        self.bot = Bot

    @commands.command(name="dm")
    async def dm_user(self, ctx: commands.Context, user: Union[discord.User, str], *args):
        """DMs a user."""
        if ctx.message.author.guild_permissions.kick_members:
            dmMsg = " ".join(args)
            if isinstance(user, str):
                await ctx.send(f"{user} isn't a valid user")
                return None
            if len(args) > 0:
                if not user.bot:
                    await user.create_dm()
                    await user.dm_channel.send(dmMsg)
                else:
                    await ctx.send(f"User {user.mention} is a bot.")
            else:
                await ctx.send(f"Can't send an empty dm.")
        else:
            await ctx.send(f"User {ctx.message.author.mention} doesn't have kick members permissions.")

    @commands.command(name="kick")
    async def kick_user(self, ctx: commands.Context, reason: str = "", *users: Union[discord.User, str]):
        """kick the pinged users out of the server and sends them a mean dm."""
        if ctx.author.guild_permissions.administrator:
            for user in users:
                if isinstance(user, str):
                    temp = user
                    try:
                        user = discord.utils.get(ctx.guild.members,
                                                 name=user.split("#")[0],
                                                 discriminator=user.split("#")[1])
                        if not isinstance(user, discord.User):
                            await ctx.send(f"{temp} isn't a valid username")
                            continue
                    except IndexError:
                        await ctx.send(f"{temp} isn't a valid username")
                        continue
                if not user.bot:
                    try:
                        await user.create_dm()
                        await ctx.guild.kick(user=user, reason=reason)
                        await user.dm_channel.send(
                            f"{user.mention} {random.choice(var.mean)}")
                    except commands.errors.CommandInvokeError:
                        await ctx.send(f"Can't kick {user}")
                else:
                    await ctx.send(f"{user.mention} is a bot, can't dm them.")
        else:
            await ctx.send(f"{ctx.author.mention} doesn't have kick members permission.")

    @commands.command(name="emoji")
    async def download_emoji(self, ctx: commands.Context, emoji: Union[discord.Emoji, str]):
        """Downloads the emoji image to the bot server files under the path
        './emojis/<guildID>/<emojiName>-<EmojiID>.png' """
        if await check_admin(ctx):
            if not isinstance(emoji, str):
                if not os.path.exists(fr'./emojis/{str(ctx.guild.id)}'):
                    os.mkdir(os.path.join(fr'./emojis/', str(ctx.guild.id)))
                with open(fr'./emojis/{str(ctx.guild.id)}/{str(emoji.name)}-{str(emoji.id)}.png', 'wb') as outputFile:
                    outputFile.write(await emoji.read())
            else:
                await ctx.send("Please specify a **custom emoji**")

    @commands.command(name="rules")
    async def edit_rules(self, ctx: commands.Context, num, *rule):
        """Add/Edit rules."""
        if await check_admin(ctx):
            newRule = " ".join(rule)
            ruleNum = int(num)
            rulesStr = ''
            data = load_data()
            if ruleNum != 0:
                if ruleNum <= len(data.get(str(ctx.guild.id))["rules"]):
                    data.get(str(ctx.guild.id))["rules"][ruleNum - 1] = newRule
                else:
                    data.get(str(ctx.guild.id))["rules"].append(newRule)
            for i in range(0, len(data.get(str(ctx.guild.id))["rules"])):
                rulesStr = f'{rulesStr}{i + 1}.\n> {data.get(str(ctx.guild.id))["rules"][i]}\n'
            channel = ctx.guild.get_channel(1035977815608270928)
            rulesMsg: discord.Message = await discord.utils.get(channel.history(limit=100))
            if rulesMsg.author == self.bot.user:
                await rulesMsg.edit(embed=discord.Embed(title="Rules", description=rulesStr, color=var.color))
            else:
                await channel.send(embed=discord.Embed(title="Rules", description=rulesStr, color=var.color))
            with open(r"./guild.json", "w") as i:
                json.dump(data, i)

    @bot.command(name="editchannel")
    async def edit_channel(self, ctx: commands.Context, channel: Union[TextChannel,
                                                                       VoiceChannel,
                                                                       StageChannel,
                                                                       ForumChannel,
                                                                       str], typeChange: str = "-n", *args):
        """edit channel."""
        if isinstance(channel, str):
            await ctx.send(f"{channel} isn't a valid channel")
            return None
        if await check_admin(ctx):

            if typeChange == "-n":
                prefixName = args[0]
                suffixName = ' '.join(e for e in args[1:])
                await channel.edit(name=f"{prefixName}{chr(12539)}{suffixName}")
            elif typeChange == "-p":
                overwrite = discord.PermissionOverwrite()
                try:
                    role = (
                        channel.guild.get_role(int(args[0])) if args[0] != "everyone" else channel.guild.default_role)
                    attr = args[1]
                    state = bool(int(args[2]))
                    overwrite.__setattr__(attr, state)
                    await channel.set_permissions(role, overwrite=overwrite)
                except AttributeError:
                    await ctx.send(f"{args[1]} isn't a valid permission")
                except discord.NotFound:
                    await ctx.send(f"{args[0]} isn't a valid role")
            elif typeChange == "-ns":
                await channel.edit(nsfw=bool(int(args[0])))


class Fun(commands.Cog):
    def __init__(self, Bot: commands.Bot):
        self.bot = Bot

    @commands.command("say")
    async def say_something(self, ctx: commands.Context, *args):
        """Make the bot say what you want"""
        await ctx.send(" ".join(args))
        await ctx.message.delete()

    @commands.command("rickroll")
    async def rickroll_someone(self, ctx: commands.Context):
        """Sends a rickroll to rickroll your friends"""
        await ctx.send(file=discord.File("rickroll-roll.gif"))
        if not ctx.channel.type == discord.ChannelType.private:
            await ctx.message.delete()


class Help(commands.Cog):
    def __init__(self, Bot: commands.Bot):
        self.bot = Bot

    @commands.command("help")
    async def get_help(self, ctx: commands.Context, *commandName: Union[str, None]):
        """Sends this help menu"""
        commandsList = [e for e in self.bot.commands]
        msg = None
        if len(commandName) > 0:
            for i in commandName:
                for command in commandsList:
                    if i == command.name:
                        msg = await ctx.send(embed=embed(title=f"Help for command **{command.name}**",
                                                         description=command.help,
                                                         color=var.color))
        else:
            commandsAll = ""
            for command in commandsList:
                commandsAll = commandsAll + f"""\n------------------\n**{command.name}**:\n{command.help if command.help is not None else 'No help'}"""
            msg = await ctx.send(embed=embed(title="Help for commands:", description=commandsAll, color=var.color))
        if msg is not None:
            await msg.delete(delay=100)
            await ctx.message.delete(delay=100)


@bot.event
async def on_ready():
    bot.remove_command("editchannel")
    await bot.add_cog(Events(bot))
    await bot.add_cog(Cash(bot))
    await bot.add_cog(Moderation(bot))
    await bot.add_cog(Fun(bot))
    await bot.add_cog(Help(bot))

    print(f'{bot.user} has connected to Discord!\n{bot.user} is connected to the following guild:')
    for guild in bot.guilds:
        data = load_data()
        if not str(guild.id) in data:
            membersListGuild = []
            for l in guild.members:
                membersListGuild.append({"name": l.name, "id": l.id, "cash": 0})
            data.update({str(guild.id): {"members": membersListGuild,
                                         "prefixes": var.defaultPrefix,
                                         "rules": var.defaultRules}})
            with open("guild.json", "w") as j:
                json.dump(data, j)
            print(data)

        print(f'---{guild.name} (id: {guild.id})\n\t---Owner: {guild.owner}. Num members: {guild.member_count}')


@bot.command()
@commands.guild_only()
async def setprefix(ctx: commands.Context, *, prefixes='$'):
    """Sets the server custom bot prefixes, can be more than one."""
    if await check_admin(ctx):
        if prefixes != '':
            try:
                bot_message = await ctx.send(embed=discord.Embed(title="Prefix Change",
                                                                 description=f"Change prefix from"
                                                                             f" {'/'.join(await var.determine_prefix(Bot=bot, message=ctx.message))} to "
                                                                             f"{'/'.join(prefixes.split())}?"
                                                                             f" React with \N{THUMBS UP SIGN}.",
                                                                 color=var.color))
                await bot_message.add_reaction('\N{THUMBS UP SIGN}')

                def check(reaction, user):
                    return user == ctx.message.author and str(reaction.emoji) == '\N{THUMBS UP SIGN}'

                try:
                    reaction, user = await bot.wait_for('reaction_add', timeout=60.0, check=check)

                except asyncio.TimeoutError:
                    await ctx.send('Timed out after 1min. Prefix change cancelled.')
                else:
                    with open(r"./guild.json", ) as i:
                        data: dict = json.load(i, )
                        data.update({str(ctx.guild.id): {"prefixes": prefixes.split()}})
                        with open("guild.json", "w") as j:
                            json.dump(data, j)
                    var.customPrefixes[ctx.guild.id] = prefixes.split() or var.defaultPrefix
                    await ctx.send(embed=discord.Embed(title="Prefix Change",
                                                       description=f"Prefix changed to "
                                                                   f"{'/'.join(prefixes.split())}.",
                                                       color=var.color))
            except IndexError:
                await ctx.send(embed=discord.Embed(title="Prefix Change",
                                                   description=f"Please specify a new prefix. current one:"
                                                               f" {await var.determine_prefix(Bot=bot, message=ctx.message)}",
                                                   color=var.color))


@bot.event
async def on_message(message: discord.Message):
    await bot.process_commands(message)
    pass


bot.run(token=var.TOKEN)
