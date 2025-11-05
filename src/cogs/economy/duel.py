from discord import app_commands, Interaction, Embed, ButtonStyle
from discord.ext import commands
from discord.ui import View, Button
import discord
import random
import asyncio

commisionPercent = 5


class DuelAcceptView(View):
    def __init__(self, command_interaction: discord.Interaction, amount: int, db):
        super().__init__(timeout=180)
        self.command_interaction = command_interaction
        self.amount = amount
        self.db = db



    @discord.ui.button(label="Принять", style=ButtonStyle.secondary)
    async def accept_button(
        self, button_interaction: discord.Interaction, button: Button
    ):
        if button_interaction.user.id == self.command_interaction.user.id:
            return

        acceptor_data = await self.db.get_user(button_interaction.user.id)
        acceptor_balance = acceptor_data["balance"]
        if acceptor_balance < self.amount:
            embed = discord.Embed(
                title="Недостаточно средств!",
                description=f"{button_interaction.user.mention}, У вас недостаточно средств.\nНе хватает: {self.amount - acceptor_balance} Монет",
                color=discord.Color.from_str("#494949"),
            )
            embed.set_thumbnail(url=self.command_interaction.user.display_avatar.url)
            await button_interaction.response.send_message(
                embed=embed, ephemeral=True
            )
            return

        initiator_data = await self.db.get_user(self.command_interaction.user.id)
        initiator_balance = initiator_data["balance"]
        if initiator_balance < self.amount:
            embed = discord.Embed(
                title="Недостаточно средств!",
                description=f"{self.command_interaction.user.mention} потратил ставку до начала дуэли...\nНе хватает: {self.amount - initiator_balance} Монет",
                color=discord.Color.from_str("#494949"),
            )
            await button_interaction.followup.edit_message(message_id=button_interaction.message.id, embed=embed, view=None)
            return

        commision = round(self.amount * (commisionPercent / 100))
        receivedAmount = self.amount - commision

        embed = Embed(
            title="Дуэль началась!",
            description=(
                f"{self.command_interaction.user.mention} и {button_interaction.user.mention} начали дуэль на **{receivedAmount}** монет!"
            ),
            color=discord.Color.from_str("#494949"),
        )

        await button_interaction.response.edit_message(embed=embed, view=None)
        await asyncio.sleep(3)

        winner, loser = random.sample([self.command_interaction, button_interaction], 2)

        
        async with self.db.get_connection() as conn:
            await self.db.plus_balance(
                winner.user.id,
                receivedAmount,
                f"Дуэль против {loser.user.mention}",
            )
            await self.db.minus_balance(
                loser.user.id,
                self.amount,
                f"Дуэль против {winner.user.mention}",
            )

        embed = Embed(
            title="Дуэль",
            description=(
                f"{winner.user.mention} победил {loser.user.mention} и выйграл **{receivedAmount}** монет!"
            ),
            color=discord.Color.from_str("#494949"),
        )
        embed.set_thumbnail(url=winner.user.display_avatar.url)

        await button_interaction.followup.edit_message(
            message_id=button_interaction.message.id, embed=embed, view=None
        )



class Duel(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.db = bot.db


    async def on_timeout(self):
        for child in self.children:
            child.disabled = True
        await self.command_interaction.edit_original_response(view=self)



    @app_commands.command(name="duel", description="Вызвать на дуэль.")
    @app_commands.describe(amount="Ставка на дуэль.")
    async def duel(
        self,
        command_interaction: Interaction,
        amount: app_commands.Range[int, 10, None],
    ):
        await command_interaction.response.defer(thinking=True)

        initiator_data = await self.db.get_user(command_interaction.user.id)
        initiator_balance = initiator_data["balance"]

        if initiator_balance < amount:
            embed = discord.Embed(
                title="Недостаточно средств!",
                description=f"{command_interaction.user.mention}, У вас недостаточно средств.\nНе хватает: {amount - initiator_balance} Монет",
                color=discord.Color.from_str("#494949"),
            )
            embed.set_thumbnail(url=command_interaction.user.display_avatar.url)
            await command_interaction.edit_original_response(embed=embed, view=None)
            return

        commision = round(amount * (commisionPercent / 100))
        receivedAmount = amount - commision

        embed = Embed(
            title="Дуэль",
            description=f"{command_interaction.user.mention} создал дуэль на **{receivedAmount}** монет.\n",
            color=discord.Color.from_str("#494949"),
        )
        embed.set_thumbnail(url=command_interaction.user.display_avatar.url)

        view = DuelAcceptView(command_interaction, amount, self.db)
        await command_interaction.followup.send(embed=embed, view=view)


async def setup(bot):
    await bot.add_cog(Duel(bot))
