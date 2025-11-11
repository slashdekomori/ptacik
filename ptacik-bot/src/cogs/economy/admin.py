from discord import app_commands, Embed, Color
from discord.ext import commands
import discord


import os
from dotenv import load_dotenv

load_dotenv()
GUILD_ID = os.getenv("GUILD_ID")


class Admin(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.db = bot.db

    @app_commands.guilds(discord.Object(id=int(GUILD_ID)))
    @app_commands.command(name="inc", description="increment")
    @app_commands.describe(amount="amount")
    @app_commands.describe(target=".")
    async def inc(
        self, interaction: discord.Interaction, amount: int, target: discord.User
    ):
        await interaction.response.defer(thinking=True)

        await self.db.plus_balance(
            target.id,
            amount,
            f"кичигин от {interaction.user.mention}",
        )

        embed = Embed(
            title="Админ",
            description=f"{interaction.user.mention} накичигинил **{amount}** монет.\n",
            color=Color.blurple(),
        )

        await interaction.followup.send(embed=embed, ephemeral=True)

    @app_commands.guilds(discord.Object(id=int(GUILD_ID)))
    @app_commands.command(name="dec", description="decrement")
    @app_commands.describe(amount="amount")
    @app_commands.describe(target=".")
    async def dec(
        self, interaction: discord.Interaction, amount: int, target: discord.User
    ):
        await interaction.response.defer(thinking=True)

        await self.db.minus_balance(
            target.id,
            amount,
            f"кичигин от {interaction.user.mention}",
        )
        embed = Embed(
            title="Админ",
            description=f"{interaction.user.mention} накичигинил **{amount}** монет.\n",
            color=Color.blurple(),
        )

        await interaction.followup.send(embed=embed, ephemeral=True)


async def setup(bot):
    await bot.add_cog(Admin(bot))
