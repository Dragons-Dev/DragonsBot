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


def sec_to_min(time: float):
    time = round(time)
    hours, seconds = divmod(time, 60 * 60)
    minutes, seconds = divmod(seconds, 60)
    if not hours:
        return f"{minutes}m {str(seconds).zfill(2)}s"
    return f"{hours}h {minutes}m {str(seconds).zfill(2)}s"

