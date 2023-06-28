import discord
from discord.ext import commands

from src import utils, db


async def complete(ctx: discord.AutocompleteContext) -> list[str]:
    possible_users = [m for m in ctx.interaction.guild.members if str(m.id).startswith(ctx.value)]
    return [f"{m.display_name} ({m.id})" for m in possible_users]


class Bans(commands.Cog):
    def __init__(self, client):
        self.client: commands.Bot = client

    @commands.slash_command(name="ban", description="Ban a user")
    async def ban(self,
                  ctx: discord.ApplicationContext,
                  member: discord.Option(
                      input_type = str,
                      autocomplete=complete
                  )):
        for role in ctx.author.roles:
            if role.permissions.ban_members or role.permissions.administrator:
                member = member[::-1]
                mem_id = ""
                for i in member:
                    if i == "(":
                        break
                    if i.isdigit():
                        mem_id = mem_id + i
                member = await utils.get_or_fetch_member(
                    member_id=int(mem_id[::-1]),
                    guild=ctx.guild,
                    client=self.client
                )
                await ctx.response.send_message(f"You want to ban {member.name}", ephemeral=True)
                break
        else:
            await ctx.response.send_message(f"You are not allowed to ban", ephemeral=True)

    @ban.before_invoke
    async def is_enabled(self, ctx: discord.ApplicationContext):
        response = await db.command_enabled(ctx.command.name, ctx.guild_id)
        if not bool(response[0]):
            return await ctx.response.send_message(f"This command is disabled at the moment.")

    @ban.error
    async def on_ban_error(self, ctx: discord.ApplicationContext, error: discord.ApplicationCommandError):
        if isinstance(error, discord.ApplicationCommandInvokeError):
            pass
        else:
            raise error


def setup(client: commands.Bot):
    client.add_cog(Bans(client))
