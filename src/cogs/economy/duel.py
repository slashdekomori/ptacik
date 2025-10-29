from discord import app_commands, Interaction, Embed, Color, ButtonStyle
from discord.ext import commands
from discord.ui import View, Button
import discord

class DuelAcceptView(View):
    def __init__(self, initiator: discord.User, amount: int, db):
        super().__init__(timeout=180)  # Duel request expires after 60 seconds
        self.initiator = initiator
        self.amount = amount
        self.db = db

    @discord.ui.button(label="Принять", style=ButtonStyle.green)
    async def accept_button(self, interaction: Interaction, button: Button):
        if interaction.user.id == self.initiator.id:
            await interaction.response.send_message(
                "Вы не можете принять собственную дуэль.", ephemeral=True
            )
            return

        acceptor = await self.db.get_user(interaction.user.id)
        if acceptor["balance"] < self.amount:
            await interaction.response.send_message(
                "Недостаточно средств для принятия дуэли.", ephemeral=True
            )
            return

        initiatorDb = await self.db.get_user(self.initiator.id)
        if initiatorDb['balance'] < self.amount:
            await interaction.response.send_message(
                "Инициатор потратил ставку до начала дуэли..."
            ) 
            return
            
        embed = Embed(
            title="Дуэль началась!",
            description=(
                f"{self.initiator.mention} и {interaction.user.mention}"
                f"начали дуэль на **{self.amount}** монет!"
            ),
            color=Color.green(),
        )

        await interaction.response.edit_message(embed=embed, view=self)
        # Here you could continue with duel logic (e.g. random winner, DB updates)


class Duel(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.db = bot.db

    @app_commands.command(
        name="duel", description="Вызвать на дуэль."
    )
    @app_commands.describe(amount="Ставка на дуэль.")
    async def duel(self, interaction: Interaction, amount: int):
        await interaction.response.defer(thinking=True)

        initiator = await self.db.get_user(interaction.user.id)
        if initiator["balance"] < amount:
            await interaction.followup.send(
                "Недостаточно средств на балансе.", ephemeral=True
            )
            return

        embed = Embed(
            title="Дуэль",
            description=f"{interaction.user.mention} создал дуэль на **{amount}** монет.\n",
            color=discord.Color.from_str("#494949"),
        )

        view = DuelAcceptView(interaction.user, amount, self.db)
        await interaction.followup.send(embed=embed, view=view)


async def setup(bot):
    await bot.add_cog(Duel(bot))
