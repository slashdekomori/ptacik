from discord import app_commands, Interaction, Embed, Color, ButtonStyle
from discord.ext import commands
from discord.ui import View, Button
import discord

import dotenv, os
ADMINS = os.getenv("ADMINS", "").split(",")

class Admin(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.db = bot.db
    
    @app_commands.command(
        name="inc", description="increment"
    )
    @app_commands.describe(amount="amount")
    @app_commands.describe(target=".")
    async def inc(self, interaction: discord.Interaction, amount: int, target: discord.User):
        await interaction.response.defer(thinking=True)

        target = self.db.plus_balance(target.id, "кичигинные свойства") 

        embed = Embed(
            title="Админ",
            description=f"{interaction.user.mention} накичигинил **{amount}** монет.\n",
            color=Color.blurple(),
        )

        await interaction.followup.send(embed=embed, ephemeral=True)

    @app_commands.command(
        name="dec", description="decrement"
    )
    @app_commands.describe(amount="amount")
    @app_commands.describe(target=".")
    async def dec(self, interaction: discord.Interaction, amount: int, target: discord.User):
        await interaction.response.defer(thinking=True)

        target = self.db.minus_balance(target.id, "кичигинные свойства") 

        embed = Embed(
            title="Админ",
            description=f"{interaction.user.mention} накичигинил **{amount}** монет.\n",
            color=Color.blurple(),
        )

        await interaction.followup.send(embed=embed, ephemeral=True)




async def setup(bot):
    await bot.add_cog(Admin(bot))
