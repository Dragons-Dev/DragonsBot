import discord
from discord.ext import commands, tasks

import time
import random

from src import db, utils


class Activity(commands.Cog):
    def __init__(self, client):
        self.client: commands.Bot = client
        self.active_members = {}
        self.active_counter.start()
        self.once = False

    @tasks.loop(seconds=15)
    async def active_counter(self):
        for member, guild in self.active_members.items():
            bank = await db.get_member_cash("pocket", member, guild)
            await db.set_member_cash("pocket", bank[0] + random.randint(1, 15), member, guild)

    @commands.Cog.listener("on_voice_state_update")
    async def activity_manager(self,
                               member: discord.Member,
                               before: discord.VoiceState,
                               after: discord.VoiceState):
        if before.channel is None:
            self.active_members[member.id] = member.guild.id
        if after.channel is None:
            try:
                del self.active_members[member.id]
            except KeyError:
                pass

    @commands.Cog.listener("on_ready")
    async def scan_active(self) -> None:
        if not self.once:
            self.once = True
            await self.client.wait_until_ready()
            for guild in self.client.guilds:
                for channel in guild.voice_channels:
                    for member in channel.members:
                        self.active_members[member.id] = guild.id


def setup(client: commands.Bot):
    client.add_cog(Activity(client))
