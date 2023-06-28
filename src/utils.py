import discord
from discord.ext import commands


async def get_or_fetch_member(
        member_id: int,
        guild: discord.Guild,
        client: commands.Bot
) -> discord.User | discord.Member:
    member = guild.get_member(member_id)
    if member is None:
        member = await client.fetch_user(member_id)
    return member
