import discord
from discord.ext import commands


class Nuke(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.slash_command(name="nuke", description="Clears a channel from messages")
    async def nuke(self, ctx: discord.ApplicationContext, amount: discord.Option(int) = 100):
        deleted = await ctx.channel.purge(limit=amount)
        await ctx.response.send_message(f"You've deleted {len(deleted)} from {amount} messages", ephemeral=True, delete_after=10)


def setup(client: commands.Bot):
    client.add_cog(Nuke(client))
