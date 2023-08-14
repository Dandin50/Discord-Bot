# IMPORTS
import calendar
import datetime
import inspect
import json
import os
import time
from typing import Union, Literal, Optional

import discord
import matplotlib.pyplot as plt
import pandas as pd
from colorama import Style
from discord import TextChannel, VoiceChannel, StageChannel, ForumChannel, app_commands, Intents
from discord.interactions import Interaction
from discord.ui import Button

import resources


# CLIENT
# region CLIENT
class Bot(discord.Client):
    def __init__(self, *, intents: Intents):
        super().__init__(intents=intents)
        self.tree = discord.app_commands.CommandTree(self)

    async def setup_hook(self) -> None:
        await self.tree.sync()


client = Bot(intents=resources.intentsOutput)
embed = discord.Embed


# endregion

# UTIL FUNCTIONS
# region UTIL FUNCTIONS
def drop(a): return a


def x(a): return Style.BRIGHT + a + Style.RESET_ALL


def process_command(interaction: Interaction):
    options = []
    try:
        for option in interaction.data['options']:
            options.append(x(f"\n\t> {option['name']} ({option['type']}): {option['value']}"))
    except:
        pass
    print(inspect.cleandoc(f"""> {x(interaction.user.name)}
    >> used the command {x(interaction.command.name)}
    >> in {x(f'{interaction.guild.name}/{interaction.channel.name}')}
    >> at {x(datetime.datetime.now().strftime('%d/%m/%Y %H:%M:%S'))}
    >> data: {''.join(options)}"""))
    return interaction


# endregion

# EVENTS
# region EVENTS
@client.event
async def on_ready():
    print(f"{Style.BRIGHT}Done starting{Style.RESET_ALL}")
    # rob = discord.utils.get(client.guilds, id=1035180091946319892).get_member(711269513991028807)
    # print(rob.display_name)
    # await rob.create_dm()
    # async for e in rob.dm_channel.history(): print(f"{e.author} - {e.content}")


@client.event
async def on_member_join(member: discord.Member):
    await member.create_dm()
    await member.dm_channel.send(embed=discord.Embed(title=f"Welcome to"
                                                           f" {member.guild.name}!",
                                                     description=f"Hi {member.mention}!"
                                                                 f" Welcome to {member.guild.name},"
                                                                 f" owned by {member.guild.owner.name}",
                                                     color=resources.color))
    # for i in member.guild.channels:
    #     if type(i) == discord.TextChannel:
    #         if member.guild.created_at.timestamp() - i.created_at.timestamp() < 5:
    #             await i.send(content=f"Welcome {member.mention}")


# endregion

# COMMANDS
# region
# region say
@client.tree.command(description="Sends a message as a the user")
@app_commands.describe(message="The message to send",
                       channel="The channel to send in. Leave empty for current channel.")
async def echo(interaction: Interaction, message: str,
               channel: Union[TextChannel, VoiceChannel, StageChannel, ForumChannel] = None):
    interaction = process_command(interaction)
    if channel is not None:
        await channel.send(message)
    else:
        await interaction.channel.send(message)
    await interaction.response.send_message("Sent!", ephemeral=True)


# endregion


# region dm

@client.tree.command(description="DM a user")
@app_commands.describe(user="User to dm", message="The message to send")
async def dm(interaction: Interaction, user: discord.User, message: str):
    interaction = process_command(interaction)
    if interaction.user.guild_permissions.kick_members:
        if not user.bot:
            await interaction.response.send_message(ephemeral=True,
                                                    view=discord.ui.View()
                                                    .add_item(Button(style=discord.ButtonStyle.green,
                                                                     label="Yes",
                                                                     custom_id="valid_dm"))
                                                    .add_item(Button(style=discord.ButtonStyle.red,
                                                                     label="No",
                                                                     custom_id="un_valid_dm")))
            print("Hi")

            res: Interaction = await client.wait_for('interaction',
                                                     check=lambda
                                                         interactiona: interactiona.type == discord.InteractionType.component and
                                                                       interactiona.data["custom_id"] in ["valid_dm",
                                                                                                          "un_valid_dm"])
            if res.data["custom_id"] == "valid_dm":
                await user.create_dm()
                await user.dm_channel.send(message)
                await interaction.edit_original_response(view=None, content="Sent!")
            else:
                await interaction.edit_original_response(view=None, content="Canceled")
        else:
            await interaction.response.send_message(f"{user} is a bot", ephemeral=True)
    else:
        await interaction.response.send_message(f"You don't have kick members permission", ephemeral=True)


# endregion


# region edit channel
@client.tree.command(description="Edit channel", name="editchannel")
@app_commands.rename(typeChange="type", prefixName="prefixname", suffixName="suffixname",
                     typeOfPrefix="typeOfPrefix".lower())
@app_commands.describe(channel="The selected channel",
                       typeChange="The type to the edit",
                       prefixName="Prefix before the dot. Requires name to be selected in type option",
                       suffixName="Suffix before the dot. Requires name to be selected in type option",
                       typeOfPrefix="The special prefix mode. Requires name to be selected in type option",
                       permission="Permission to toggle. Requires permissions to be selected in type option",
                       state="True/False. Requires permissions or nsfw to be selected in type option",
                       role="Selected role. Requires permissions to be selected in type option")
async def edit_channel(interaction: Interaction,
                       channel: TextChannel,
                       typeChange: Literal["name", "permissions", "nsfw"],
                       prefixName: Optional[str],
                       suffixName: Optional[str],
                       typeOfPrefix: Optional[Literal["「」", '・']],
                       permission: Optional[resources.validPermissions],
                       state: Optional[Literal["True", "False", "Remove"]],
                       role: Optional[discord.Role]):
    interaction = process_command(interaction)
    if await resources.check_admin(interaction=interaction):
        if typeChange == "name":
            for i in [prefixName, suffixName]:
                if i is None:
                    await interaction.response.send_message(f"Please specify prefix and suffix", ephemeral=True)
                    return 0
            if typeOfPrefix == '・' or typeOfPrefix is None:
                await channel.edit(name=f"{prefixName}{chr(12539)}{suffixName}")
            elif typeOfPrefix == "「」":
                await channel.edit(name=f"{chr(12300)}{prefixName}{chr(12301)}{suffixName}")
        elif typeChange == "permissions":
            for i in [permission, role, state]:
                if i is None:
                    await interaction.response.send_message(f"Please specify permission, state and role",
                                                            ephemeral=True)
                    return 0
            overwrite = discord.PermissionOverwrite()
            overwrite.__setattr__(permission, resources.change.get(state))
            if role == "everyone":
                role = interaction.guild.default_role

            await channel.set_permissions(role, overwrite=overwrite)
        elif typeChange == "nsfw":
            if state is None:
                await interaction.response.send_message(f"Please specify state", ephemeral=True)
                return 0
            await channel.edit(nsfw=(resources.change.get(state) if resources.change.get(state) is not None else False))
        await interaction.response.send_message("Done!", ephemeral=True)


# endregion


# region Rickroll
@client.tree.command(name="rickroll", description="Rickroll everyone in chat!")
@app_commands.guild_only
@app_commands.describe(channel="Specify channel", spoiler="Set file as spoiler")
async def rickroll(interaction: Interaction, channel: Optional[discord.TextChannel], spoiler: bool = False):
    interaction = process_command(interaction)
    rickrollFile = discord.File("rickroll-roll.gif", spoiler=spoiler)
    if channel is not None:
        if channel.permissions_for(interaction.message.author).send_messages:
            await channel.send(file=rickrollFile)
        else:
            await interaction.response.send_message(f"You don't have permissions to send messages in {channel.mention}",
                                                    ephemeral=True)
    else:
        await interaction.channel.send(file=rickrollFile)
    await interaction.response.send_message("Done!", ephemeral=True)


# endregion


# region get cash
@client.tree.command(name="getcash", description="Get user's cash")
@app_commands.describe(user="User")
async def getcash(interaction: Interaction, user: discord.User):
    interaction = process_command(interaction)
    for memberData in resources.load_data([str(interaction.guild.id), "members"]):
        if memberData.get("id") == user.id:
            await interaction.response.send_message(f"The cash for {user.display_name.capitalize()} "
                                                    f"is: {memberData.get('cash')}")
            break


# endregion


# region set cash
@client.tree.command(name="setcash", description="Set user's cash")
@app_commands.describe(user="User", amount="Amount of cash")
async def setcash(interaction: Interaction, user: discord.User, amount: int):
    interaction = process_command(interaction)
    if resources.check_admin(interaction):
        membersData = resources.load_data([str(interaction.guild.id), "members"])
        for memberIndex in range(len(membersData)):
            if membersData[memberIndex].get("id") == user.id:
                data = resources.load_data()
                data.get(str(interaction.guild.id)).get("members")[memberIndex]["cash"] = amount
                await interaction.response.send_message(f'{user.display_name.capitalize()} cash is now {amount}',
                                                        ephemeral=True)
                with open(r"./guild.json", "w") as i:
                    json.dump(data, i)
                break


# endregion


# region kick
@client.tree.command(name="kick", description="Kick a user")
@app_commands.describe(user="User to kick", reason="Reason for the kick")
async def kick_user(interaction: Interaction, user: discord.User, reason: Optional[str]):
    interaction = process_command(interaction)
    if interaction.user.guild_permissions.kick_members:
        await interaction.guild.kick(user=user, reason=reason)
        await interaction.response.send_message(f"Kicked {user.display_name.capitalize()} successfully", ephemeral=True)


# endregion


# region edit rules
@client.tree.command(name="editrules", description="Edit the server rules")
@app_commands.rename(rule_num="rulenumber", new_rule="newrule")
async def edit_rules(interaction: Interaction, rule_num: resources.rulesLength, new_rule: str):
    interaction = process_command(interaction)
    if await resources.check_admin(interaction):
        rulesStr = ''
        data = resources.load_data()
        if new_rule != "-del":
            if rule_num <= len(data.get(str(interaction.guild.id))["rules"]):
                data.get(str(interaction.guild.id))["rules"][rule_num - 1] = new_rule
            else:
                data.get(str(interaction.guild.id))["rules"].append(new_rule)
        else:
            data.get(str(interaction.guild.id))["rules"].pop(rule_num - 1)
        for i in range(0, len(data.get(str(interaction.guild.id))["rules"])):
            rulesStr = f'{rulesStr}{i + 1}.\n> {data.get(str(interaction.guild.id))["rules"][i]}\n'
        channel = interaction.guild.get_channel(1035977815608270928)
        rulesMsg: discord.Message = await discord.utils.get(channel.history(limit=100))
        if rulesMsg.author == client.user:
            await rulesMsg.edit(embed=discord.Embed(title="Rules", description=rulesStr, color=resources.color))
        else:
            await channel.send(embed=discord.Embed(title="Rules", description=rulesStr, color=resources.color))
        with open(r"./guild.json", "w") as i:
            json.dump(data, i)


# endregion


# region join stats
@client.tree.command(description="Get server amount of members per time in graph")
@app_commands.describe(year="The year for data (leave blank for all)",
                       month="The month for data (leave blank for year)",
                       day="The day for data (leave blank for month)",
                       accuracy="Data accuracy (in seconds)")
async def memberstats(interaction: Interaction, year: Optional[int], month: Optional[resources.monthsList],
                      day: Optional[int], accuracy: Optional[int], style: Optional[resources.styles]):
    interaction = process_command(interaction)
    await interaction.response.send_message("Loading...")
    start = interaction.guild.created_at
    end = datetime.datetime.now()
    if isinstance(year, int):
        now = datetime.datetime.now()
        if year < interaction.guild.created_at.year:
            await interaction.edit_original_response(content=f"Year {year} is before the server creation")
            return 0
        elif year > now.year:
            await interaction.edit_original_response(content=f"Year {year} is after the current year")
            return 0
        if isinstance(month, str):
            monthNum = resources.months[month]
            if year == interaction.guild.created_at.year and monthNum < interaction.guild.created_at.month:
                await interaction.edit_original_response(content=f"Month {month}/{year} is before the server creation")
                return 0
            elif year == now.year and monthNum > now.month:
                await interaction.edit_original_response(content=f"Month {month}/{year} is after the current month")
                return 0
            if isinstance(day, int):
                if 1 <= day <= calendar.monthrange(year, monthNum)[1]:
                    if year == interaction.guild.created_at.year and monthNum == interaction.guild.created_at.month and day < interaction.guild.created_at.day:
                        await interaction.edit_original_response(
                            content=f"Day {day}/{month}/{year} is before the server creation")
                        return 0
                    elif year == now.year and monthNum == now.month and day > now.day:
                        await interaction.edit_original_response(
                            content=f"Day {day}/{month}/{year} is after the current day")
                        return 0
                    else:
                        start = datetime.datetime(year=year, month=monthNum, day=day, hour=0, minute=1)
                        end = datetime.datetime(year=year, month=monthNum, day=day,
                                                hour=23, minute=59)
                else:
                    await interaction.edit_original_response(content=f"Day {day} is invalid for {month}/{year}")
                    return 0
            else:
                start = datetime.datetime(year=year, month=monthNum, day=1, hour=0, minute=1)
                end = datetime.datetime(year=year, month=monthNum, day=calendar.monthrange(year, monthNum)[1], hour=23,
                                        minute=59)
        else:
            start = datetime.datetime(year=year, month=1, day=1, hour=0, minute=1)
            end = datetime.datetime(year=year, month=12, day=calendar.monthrange(year, 12)[1], hour=23,
                                    minute=59)

    amountUsers = []
    days = []
    months = []
    accuracy = accuracy if accuracy is not None else 3600
    style = style if style is not None else 'default'
    plt.style.use(style)
    for i in range(int(start.timestamp()), int(end.timestamp()), accuracy):
        amount = 0
        Time = datetime.datetime.fromtimestamp(float(i))

        for member in interaction.guild.members:
            if member.joined_at.timestamp() < i:
                amount = amount + 1
        amountUsers.append(amount)
        months.append(f"{Time.month}\\{str(Time.year)[-2:]}")
        days.append(Time)
    df = pd.DataFrame({"amount": amountUsers, "days": days})
    # sns.relplot(
    #     data=df, kind="line",
    #     x="days", y="amount", col="month"
    # )
    fig, ax = plt.subplots(1, 1, figsize=(6, 4))
    drop(fig)
    drop(ax)
    plt.plot_date(df["days"], df["amount"], '-')
    plt.gcf().autofmt_xdate()
    plt.xlabel('Date')
    plt.ylabel('Members')
    os.remove("./plot.png")
    plt.savefig("./plot.png")
    await interaction.edit_original_response(content="Done!", attachments=[discord.File("./plot.png")])


# endregion


# region user stats
@client.tree.command()
async def userstats(interaction: Interaction, user: Optional[discord.User]):
    await interaction.response.send_message(content="Loading...")
    user: discord.User = user if user is not None else interaction.user
    user: discord.Member = await interaction.guild.fetch_member(user.id)
    permissions = [f"\n> \t{'✅' if e[1] else '❌'} {e[0].replace('_', ' ').capitalize()}" for e in
                   user.guild_permissions]
    print(permissions)
    roles = [f"\n> \t{e.mention}" for e in user.roles]
    await interaction.edit_original_response(content=None, embed=discord.Embed(
        title=f"Showing data for {user.mention}",
        description=f"**Username**: \n> {user}\n\n"
                    f"**Nickname**: \n> {user.display_name}\n\n"
                    f"**Bot?**: \n> {user.bot}\n\n"
                    f"**Joined Server Date**: \n> <t:{int(user.joined_at.timestamp())}:F>\n\n"
                    f"**Joined Discord Date**: \n> <t:{int(user.created_at.timestamp())}:F>\n\n"
                    f"**ID**: \n> {user.id}\n\n"
                    f"**Roles** (total {len(roles)}): {''.join(roles[::-1])}\n\n"
                    f"**Permissions**: {''.join(permissions)}"
    ).set_author(name=user.name, icon_url=user.avatar.url))


# endregion
@client.tree.command(description="Get the timestamp of a certain date")
@app_commands.describe(year="Leave empty for current year", month="Leave empty for current month",
                       day="Leave empty for current day", hour="Leave empty for current hour",
                       minute="Leave empty for current minute", second="Leave empty for current second",
                       microsecond="Leave empty for current microsecond")
async def timestamp(interaction: Interaction, year: Optional[int], month: Optional[resources.monthsList],
                    day: Optional[int], hour: Optional[int], minute: Optional[int], second: Optional[int],
                    microsecond: Optional[int]):
    now = datetime.datetime.now()
    if year is None: year = now.year
    if month is None:
        month = now.month
    else:
        month = resources.months[month]
    if day is None: day = now.day
    if hour is None: hour = now.hour
    if minute is None: minute = now.minute
    if second is None: second = now.second
    if microsecond is None: microsecond = now.microsecond
    # if not 0 < day < calendar.monthrange(year, month)[1] + 1:
    #     await interaction.edit_original_response(content=f"Day {day} is invalid for {month}/{year}")
    #     return 0
    # if not 0 <= hour < 24
    try:
        time = datetime.datetime(year, month, day, hour, minute, second, microsecond)
    except Exception as e:
        await interaction.response.send_message(e)
        return 0
    await interaction.response.send_message(content=f"{time.timestamp()}\n{int(time.timestamp())}")
    return 0


@client.tree.command()
async def setup_k1n9kn19ht(interaction: Interaction):
    if interaction.guild.id != 1140694739142852750:
        return
    a = 0
    await interaction.response.send_message("starting")
    role = interaction.guild.get_role(1140696889675743233)
    for channel in interaction.guild.channels:
        if channel.permissions_for(
                interaction.guild.default_role).read_messages and channel.category_id != 1140695746715320421:
            print(channel.name, type(channel), channel.permissions_for)
            await interaction.edit_original_response(content=channel.mention)
            await channel.set_permissions(role, read_messages=True)
            await channel.set_permissions(interaction.guild.default_role, read_messages=False)
            a += 1
    await interaction.edit_original_response(content=f"finished with {a} channel")


# endregion
@client.tree.command()
async def delete_bot_msgs(interaction: Interaction):
    for channel in interaction.guild.channels:
        if type(channel) in [TextChannel, VoiceChannel]:
            msg = await discord.utils.get(channel.history(limit=100))
            if msg is not None:
                if msg.author == client.user:
                    await msg.delete()


print("hi")

client.run(token=resources.TOKEN)
