import datetime
import time
import typing as t

import discord
from discord.ext import commands

from src import db, utils


class CashInOutModal(discord.ui.Modal):
    def __init__(self, target: t.Literal["pocket", "bank"], amount, *args, **kwargs) -> None:
        self.target = target
        self.amount = amount
        super().__init__(*args, **kwargs)
        x = {
            "bank": "pocket",
            "pocket": "bank"
        }
        self.add_item(discord.ui.InputText(
            label=f"You have {utils.beautify_cash(self.amount)} CDC in your {x[self.target]}")
        )

    async def callback(self, interaction: discord.Interaction):
        value = self.children[0].value.replace(",", ".")
        try:
            parts = value.split(".")
            if len(parts) > 2:
                raise ValueError
            if len(parts[1]) > 2:
                raise ValueError
            value = int(float(value) * 100)  # Userinput
        except ValueError:
            return await interaction.response.send_message("Input not valid.", ephemeral=True, delete_after=10)
        except IndexError:
            value = int(float(value) * 100)
            pass

        bank = await db.get_member_cash("bank", interaction.user.id, interaction.guild_id)
        pocket = await db.get_member_cash("pocket", interaction.user.id, interaction.guild_id)
        # withdraw
        if self.target == "pocket":
            if bank[0] - value >= 0:
                bank = bank[0] - value
                pocket = pocket[0] + value
                await db.set_member_cash("bank", bank, interaction.user.id, interaction.guild_id)
                await db.set_member_cash("pocket", pocket, interaction.user.id, interaction.guild_id)
            else:
                await interaction.response.send_message("Konto nicht gedeckt", ephemeral=True, delete_after=10)
                return
        # deposit
        else:
            if pocket[0] - value >= 0:
                bank = bank[0] + value
                pocket = pocket[0] - value
                await db.set_member_cash("bank", bank, interaction.user.id, interaction.guild_id)
                await db.set_member_cash("pocket", pocket, interaction.user.id, interaction.guild_id)
            else:
                await interaction.response.send_message("Pocket nicht gedeckt", ephemeral=True, delete_after=10)
                return
        bank = bank
        pocket = pocket
        em = discord.Embed(
            title="Bank Statement",
            description=f"Pocket" + " | " + f"{utils.beautify_cash(pocket)} CDC" + "\n"
                        f"Bank  " + " | " + f"{utils.beautify_cash(bank)} CDC",
            color=discord.Color.dark_orange()
        )
        em.set_author(name=interaction.user.display_name, icon_url=interaction.user.display_avatar)
        em.set_footer(text="Sincerely your CheesyDragon Bank")
        em.set_thumbnail(url=interaction.client.assets.BankIcon)
        await interaction.response.send_message(embed=em, ephemeral=True, delete_after=10)


class Cash(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.slash_command(name="daily-reward", description="claim your daily reward")
    @commands.cooldown(1, 86400, commands.BucketType.user)
    async def daily_reward(self, ctx: discord.ApplicationContext):
        cash = await db.get_member_cash(target="pocket", user=ctx.author.id, guild=ctx.guild_id)
        cash = cash[0]
        cash += 25
        await db.set_member_cash(target="pocket", user=ctx.author.id, guild=ctx.guild_id, amount=cash)
        await ctx.response.send_message(f"You now have {cash} CDC in your pocket.", ephemeral=True, delete_after=10)

    @daily_reward.error
    async def error(self, ctx: discord.ApplicationContext, error: discord.ApplicationCommandError):
        if isinstance(error, commands.CommandOnCooldown):
            cooldown = ctx.command.get_cooldown_retry_after(ctx)
            until = datetime.datetime.fromtimestamp(time.time() + cooldown)
            await ctx.response.send_message(f"Your daily reward is on cooldown, come back "
                                            f"{discord.utils.format_dt(until, 'R')}", ephemeral=True, delete_after=10)
        else:
            raise error

    @commands.slash_command(name="wallet", description="see your money from your pocket and your bank")
    async def wallet(self, ctx: discord.ApplicationContext):
        bank = await db.get_member_cash(target="bank", user=ctx.author.id, guild=ctx.guild_id)
        pocket = await db.get_member_cash(target="pocket", user=ctx.author.id, guild=ctx.guild_id)
        em = discord.Embed(
            title="Bank Statement",
            description=f"Pocket" + " | " + f"{utils.beautify_cash(pocket[0])} CDC" + "\n"
                        f"Bank  " + " | " + f"{utils.beautify_cash(bank[0])} CDC",
            color=discord.Color.dark_orange()
        )
        em.set_author(name=ctx.author.display_name, icon_url=ctx.author.display_avatar)
        em.set_footer(text="Sincerely your CheesyDragon Bank")
        em.set_thumbnail(url=self.client.assets.BankIcon)
        await ctx.response.send_message(embed=em, ephemeral=True, delete_after=10)

    @commands.slash_command(name="deposit", description="deposit your money to the bank")
    async def deposit(self, ctx: discord.ApplicationContext):
        amount = await db.get_member_cash(
            target="pocket",
            user=ctx.author.id,
            guild=ctx.guild_id
        )
        await ctx.response.send_modal(CashInOutModal(
            title="Deposit Money",
            target="bank",
            amount=amount[0]
        ))

def setup(client: commands.Bot):
    client.add_cog(Cash(client))
