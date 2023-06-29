import discord
from discord.ext import commands


class Credits(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.slash_command(name = "credits", description="Credits to tools helping to create this bot.")
    async def credits(self, ctx: discord.ApplicationContext):
        em1 = discord.Embed(
            title="Page 1",
            description=
"""
Icons by <https://iconpacks.net/?utm_source=link-attribution&utm_content=1071>
"""
        )
        await ctx.response.send_message(
            embeds=[em1]
        )


def setup(client: commands.Bot):
    client.add_cog(Credits(client))
