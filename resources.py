import os
from datetime import timedelta
import json
from typing import Literal, List, Tuple, Union
import enum
import matplotlib.pyplot as plt
from discord.ext import commands
import discord
from dotenv import load_dotenv

mean = ["bye you annoying person",
        "cya never lol",
        "hate u too <3",
        "apparently the stuff didn't care enough about u to keep u there",
        "I really don't care"]
context = commands.Context
defaultPrefix = "$"
customPrefixes = {}
color = 0xff4400
intents = discord.Intents.default()
intents.messages = True
intents.typing = True
intents.reactions = True
intents.presences = False
intents.message_content = True
intents.members = True
intentsOutput = intents
change = {
    "False": False,
    "True": True,
    "Remove": None
}
permissionOver = ['view_channel',
                  'manage_channels',
                  'manage_permissions',
                  'manage_webhooks',
                  'create_instant_invite',
                  'send_messages',
                  'send_messages_in_threads',
                  'create_public_threads',
                  'create_private_threads',
                  'embed_links',
                  'attach_files',
                  'add_reactions',
                  'use_external_emojis',
                  'use_external_stickers',
                  'mention_everyone',
                  'manage_messages',
                  'manage_threads',
                  'read_message_history',
                  'send_tts_messages',
                  'use_application_commands']
validPermissions = eval("Literal['" + "', '".join(permissionOver) + "']")
# validPermissions = "Literal["
# for i in permissionOver:
#     validPermissions = f"{validPermissions}'{i}',"
# validPermissions = validPermissions[:-1] + "]"
#  = eval(validPermissions)
# def validPermissions():
#     return [e for e in discord.PermissionOverwrite.VALID_NAMES]


defaultRules = ["No spamming. Allowed in <#1035259343832096868>.",
                "Use common sense and be respectful to others.",
                "No excessive swearing",
                "**NO NSFW**. Allowed in <#1052254975067181116>, for the role dm one of the <@&1035180532943814666>",
                "Being polar bear isn't allowed",
                "Don't dox people without their express permission"]
load_dotenv()

monthsList = eval('Literal["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"]')

months = {
    "January": 1,
    "February": 2,
    "March": 3,
    "April": 4,
    "May": 5,
    "June": 6,
    "July": 7,
    "August": 8,
    "September": 9,
    "October": 10,
    "November": 11,
    "December": 12
}
styles = eval(f"Literal{plt.style.available[:-3]}")
def load_data(data: list = None):
    with open(r"./guild.json", "r") as i:
        try:
            output = json.load(i, )
        except json.decoder.JSONDecodeError:
            return None
        if data:
            for j in data:
                output = output[j]
        return output


# rulesLength = lambda a: eval(f'Literal[{", ".join(str(e + 1) for e in range(len(load_data().get(str(a))["rules"])))}]')
rulesLength = eval(f'Literal[{", ".join(str(e + 1) for e in range(25))}]')


async def check_admin(interaction: discord.Interaction):
    isAdmin = interaction.user.guild_permissions.administrator
    if not isAdmin:
        timeOut: timedelta = timedelta(seconds=10)
        await interaction.response.send_message("You're not an admin", ephemeral=True)
        await interaction.message.author.author.edit(timed_out_until=discord.utils.utcnow() + timeOut,
                                                     reason="Trying to be an admin")
    return isAdmin


async def determine_prefix(Bot, message: discord.Message):
    if message.channel.type != discord.ChannelType.private:
        return load_data([str(message.guild.id)]).get("prefixes", ["$"])
    return "$"


TOKEN = os.getenv('DISCORD_TOKEN')
GUILD = os.getenv('DISCORD_GUILD')
