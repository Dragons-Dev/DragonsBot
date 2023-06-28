import discord
from discord.ext import commands

from src import db, utils


class Cash(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.slash_command(name="daily-reward", description="claim your daily reward")
    @commands.cooldown(1, 86400, commands.BucketType.user)
    async def daily_reward(self, ctx: discord.ApplicationContext):
        cash = await db.get_member_cash(
            user=ctx.author.id,
            guild=ctx.guild_id
        )
        cash = cash[0]
        cash += 25
        await db.set_cash(
            cash=cash,
            user=ctx.author.id,
            guild=ctx.guild_id
        )
        await ctx.response.send_message(f"You now have {cash} amount")


    @daily_reward.error
    async def error(self, ctx: discord.ApplicationContext, error: discord.ApplicationCommandError):
        if isinstance(error, commands.CommandOnCooldown):
            cooldown = ctx.command.get_cooldown_retry_after(ctx)
            await ctx.response.send_message(f"Your daily reward is on cooldown, come back in {utils.sec_to_min(cooldown)}")


def setup(client: commands.Bot):
    client.add_cog(Cash(client))
