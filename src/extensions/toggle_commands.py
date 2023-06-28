import discord
from discord.ext import commands

from src import utils, db


async def complete(ctx: discord.AutocompleteContext) -> list[str]:
    return [c.name for c in ctx.bot.walk_application_commands() if c.name.startswith(ctx.value)]


class Confirmation(discord.ui.View):
    @discord.ui.button(label = "Confirm", style=discord.ButtonStyle.green)
    async def confirm(self, button: discord.ui.Button, interaction: discord.Interaction):
        await interaction.response.send_message(f"You've confirmed the kick")
        button.disabled = True
        await self.message.edit(view = self)
        self.stop()


class Toggle(commands.Cog):
    def __init__(self, client):
        self.client: commands.Bot = client

    @commands.slash_command(name="toggle-command", description="toggles a command on or off")
    async def toggle(self,
                     ctx: discord.ApplicationContext,
                     command: discord.Option(
                      input_type=str,
                      autocomplete=complete
                     ),
                     enabled: discord.Option(bool)):
        for role in ctx.author.roles:
            if role.permissions.administrator:
                if command == ctx.command.name:
                    return await ctx.response.send_message(f"You may not toggle this command", ephemeral=True)
                await db.command_enabled(
                    command=command,
                    guild=ctx.guild_id,
                    enabled=bool(enabled)
                )
                await ctx.response.send_message(f"Toggled {command} {'on' if enabled is True else 'off'}",
                                                ephemeral=True)
                break
        else:
            await ctx.response.send_message(f"You are not allowed to toggle commands", ephemeral=True)


def setup(client: commands.Bot):
    client.add_cog(Toggle(client))
