import discord
from discord.ext import commands

from src import db, utils

import random

class Casino(commands.Cog):
    ...


def setup(client: commands.Bot):
    client.add_cog(Casino(client))