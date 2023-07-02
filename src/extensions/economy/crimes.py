import discord
from discord.ext import commands

from src import db, utils

import datetime
import random
import time


class Crimes(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.slash_command(name="rob", description="rob another player")
    @commands.cooldown(1, random.randint(60,600), commands.BucketType.user)
    async def rob(self,
                  ctx: discord.ApplicationContext,
                  user: discord.Option(
                      input_type=discord.SlashCommandOptionType.user
                  )):
        user = await utils.get_or_fetch_member(
            member_id=int(user.strip("<@>")),
            guild=ctx.guild,
            client=self.client
        )

        if random.randint(0, 20) == 5 or 5 == 5:
            receiver = await db.get_member_cash("pocket", ctx.user.id, ctx.guild_id)
            sender = await db.get_member_cash("pocket", user.id, ctx.guild_id)
            amount = int(sender[0] * ((random.randint(1, 10))/100))

            await db.set_member_cash("pocket", sender[0] - amount, user.id, ctx.guild_id)
            await db.set_member_cash("pocket", receiver[0] + amount, ctx.user.id, ctx.guild_id)

            await ctx.response.send_message(f"You've robbed {utils.beautify_cash(amount)} CDC from {user.display_name}.")
        else:
            await ctx.response.send_message(
                f"{ctx.author.mention} failed to rob {user.display_name}.")

    @rob.error
    async def error(self, ctx: discord.ApplicationContext, error: discord.ApplicationCommandError):
        if isinstance(error, commands.CommandOnCooldown):
            cooldown = ctx.command.get_cooldown_retry_after(ctx)
            until = datetime.datetime.fromtimestamp(time.time() + cooldown)
            await ctx.response.send_message(f"You can't rob right now, try again "
                                            f"{discord.utils.format_dt(until, 'R')}", ephemeral=True, delete_after=10)
        else:
            raise error


def setup(client: commands.Bot):
    client.add_cog(Crimes(client))
