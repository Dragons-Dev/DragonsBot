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
        cash += 2500
        await db.set_member_cash(target="pocket", user=ctx.author.id, guild=ctx.guild_id, amount=cash)
        await ctx.response.send_message(f"You now have {utils.beautify_cash(cash)} CDC in your pocket.", ephemeral=True, delete_after=10)

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

    @commands.slash_command(name="withdraw", description="withdraw money from your bank")
    async def withdraw(self, ctx: discord.ApplicationContext):
        amount = await db.get_member_cash(
            target="bank",
            user=ctx.author.id,
            guild=ctx.guild_id
        )
        await ctx.response.send_modal(CashInOutModal(
            title="Withdraw Money",
            target="pocket",
            amount=amount[0]
        ))

    @commands.slash_command(name="pay", description="pay someone from your bank")
    async def pay(self,
                  ctx: discord.ApplicationContext,
                  recipient: discord.Option(
                      input_type=discord.SlashCommandOptionType.user
                  ),
                  amount: str):  # <@342059890187173888>
        recipient = await utils.get_or_fetch_member(
            member_id=int(recipient.strip("<@>")),
            guild=ctx.guild,
            client=self.client
        )
        sender = await db.get_member_cash("bank", ctx.user.id, ctx.guild_id)
        receiver = await db.get_member_cash("bank", recipient.id, ctx.guild_id)

        amount = amount.replace(",", ".")
        try:
            parts = amount.split(".")
            if len(parts) > 2:
                raise ValueError
            if len(parts[1]) > 2:
                raise ValueError
            amount = int(float(amount) * 100)  # Userinput
        except ValueError:
            await ctx.response.send_message("Input not valid", ephemeral=True, delete_after=10)
        except IndexError:
            amount = int(float(amount)*100)

        await db.set_member_cash("bank", sender[0] - amount, ctx.user.id, ctx.guild_id)
        await db.set_member_cash("bank", receiver[0] + amount, recipient.id, ctx.guild_id)

        await ctx.response.send_message(f"You've sent {utils.beautify_cash(amount)} CDC to {recipient.display_name}.",
                                        ephemeral=True,
                                        delete_after=10)


def setup(client: commands.Bot):
    client.add_cog(Cash(client))
