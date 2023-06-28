import discord
from discord.ext import commands

from src import utils


async def complete(ctx: discord.AutocompleteContext) -> list[str]:
    possible_users = [m for m in ctx.interaction.guild.members if str(m.id).startswith(ctx.value)]
    return [f"{m.display_name} ({m.id})" for m in possible_users]


class Confirmation(discord.ui.View):
    @discord.ui.button(label = "Confirm", style=discord.ButtonStyle.green)
    async def confirm(self, button: discord.ui.Button, interaction: discord.Interaction):
        await interaction.response.send_message(f"You've confirmed the kick")
        button.disabled = True
        await self.message.edit(view = self)
        self.stop()


class Kicks(commands.Cog):
    def __init__(self, client):
        self.client: commands.Bot = client

    @commands.slash_command(name="kick", description="Kick a user")
    async def kick(self,
                   ctx: discord.ApplicationContext,
                   member: discord.Option(
                      input_type = str,
                      autocomplete=complete
                   )):
        for role in ctx.author.roles:
            if role.permissions.kick_members or role.permissions.administrator:
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
                await ctx.response.send_message(f"You want to kick {member.name}", view = Confirmation() )
                break
        else:
            await ctx.response.send_message(f"You are not allowed to kick", ephemeral=True)


def setup(client: commands.Bot):
    client.add_cog(Kicks(client))
