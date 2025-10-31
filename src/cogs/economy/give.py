import discord
from discord import app_commands
from discord.ext import commands


commisionPercent = 5


class View(discord.ui.View):
    def __init__(self, db, initiatorInteraction, target_user, amount, timeout=180):
        super().__init__(timeout=timeout)
        self.db = db
        self.initiatorInteraction = initiatorInteraction
        self.target_user = target_user
        self.amount = amount

    async def on_timeout(self):
        """Called automatically when 180 seconds pass with no interaction."""
        commision = round(self.amount * (commisionPercent / 100))
        receivedAmount = self.amount - commision

        embed = discord.Embed(
            title="Передать монеты",
            description=f"{self.initiatorInteraction.user.mention}, вы отказались передавать {receivedAmount} монет пользователю {self.target_user.mention}",
            color=discord.Color.from_str("#494949"),
        )
        embed.set_thumbnail(url=self.initiatorInteraction.user.display_avatar.url)

        try:
            await self.initiatorInteraction.edit_original_response(embed=embed, view=None)
        except discord.InteractionResponded:
            await self.initiatorInteraction.followup.send(embed=embed, view=None)

    @discord.ui.button(label="Подтвердить", style=discord.ButtonStyle.secondary)
    async def accept_callback(
        self, interaction: discord.Interaction, button: discord.ui.button
    ):
        if interaction.user.id != self.initiatorInteraction.user.id:
            return

        dbUser = await self.db.get_user(self.initiatorInteraction.user.id)
        balance = dbUser["balance"]

        if balance < self.amount:
            embed = discord.Embed(
                title="Недостаточно средств!",
                description=f"{self.initiatorInteraction.user.mention}, У вас недостаточно средств.\nНе хватает: {self.amount - balance} Монет",
                color=discord.Color.from_str("#494949"),
            )
            embed.set_thumbnail(url=self.initiatorInteraction.user.display_avatar.url)
            await interaction.response.edit_message(embed=embed, view=None)
            return

        commision = round(self.amount * (commisionPercent / 100))
        receivedAmount = self.amount - commision

        await self.db.plus_balance(
            self.target_user.id,
            receivedAmount,
            f"Получено от {self.initiatorInteraction.user.mention}",
        )
        await self.db.minus_balance(
            self.initiatorInteraction.user.id,
            self.amount,
            f"Передано пользователю {self.initiatorInteraction.user.mention}",
        )

        embed = discord.Embed(
            title="Передать монеты",
            description=f"{self.initiatorInteraction.user.mention}, вы передали {receivedAmount} монет пользователю {self.target_user.mention}",
            color=discord.Color.from_str("#494949"),
        )
        embed.set_thumbnail(url=self.initiatorInteraction.user.display_avatar.url)

        await interaction.response.edit_message(content=None, view=None, embed=embed)

    @discord.ui.button(label="Отмена", style=discord.ButtonStyle.danger)
    async def cancel_callback(
        self, interaction: discord.Interaction, button: discord.ui.button
    ):
        if interaction.user.id != self.initiatorInteraction.user.id:
            return

        commision = round(self.amount * (commisionPercent / 100))
        receivedAmount = self.amount - commision

        embed = discord.Embed(
            title="Передать монеты",
            description=f"{self.initiatorInteraction.user.mention}, вы отказались передавать {receivedAmount} монет пользователю {self.target_user.mention}",
            color=discord.Color.from_str("#494949"),
        )
        embed.set_thumbnail(url=self.initiatorInteraction.user.display_avatar.url)

        await interaction.response.edit_message(content=None, view=None, embed=embed)


class Give(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.db = bot.db

    @app_commands.command(name="give", description="Передать монеты.")
    @app_commands.describe(
        target_user="Пользователь которому хотите передать монеты.", amount="Количество"
    )
    async def give(
        self,
        interaction: discord.Interaction,
        target_user: discord.User,
        amount: app_commands.Range[int, 10, None],
    ):
        await interaction.response.defer(thinking=True)

        if target_user.bot:
            embed = discord.Embed(
                title="Передать монеты",
                description=f"{interaction.user.mention}, нельзя перевести монеты боту.",
                color=discord.Color.from_str("#494949"),
            )
            embed.set_thumbnail(url=interaction.user.display_avatar.url)
            await interaction.followup.send(embed=embed)
            return

        if target_user.id == interaction.user.id:
            embed = discord.Embed(
                title="Передать монеты",
                description=f"{interaction.user.mention}, нельзя перевести монеты самому себе.",
                color=discord.Color.from_str("#494949"),
            )
            embed.set_thumbnail(url=interaction.user.display_avatar.url)
            await interaction.followup.send(embed=embed)
            return

        commision = round(amount * (commisionPercent / 100))
        receivedAmount = amount - commision

        dbUser = await self.db.get_user(interaction.user.id)
        balance = dbUser["balance"]

        if balance < amount:
            embed = discord.Embed(
                title="Недостаточно средств!",
                description=f"{interaction.user.mention}, У вас недостаточно средств \nНе хватает: {amount - balance} Монет",
                color=discord.Color.from_str("#494949"),
            )
            embed.set_thumbnail(url=interaction.user.display_avatar.url)
            await interaction.followup.send(embed=embed)
            return

        embed = discord.Embed(
            title="Передать монеты",
            description=f"{interaction.user.mention}, вы уверены что хотите передать {receivedAmount} монет, включая комиссию 5% пользователю {target_user.mention}?",
            color=discord.Color.from_str("#494949"),
        )
        embed.set_thumbnail(url=interaction.user.display_avatar.url)

        await interaction.followup.send(
            embed=embed, view=View(self.db, interaction, target_user, amount)
        )


async def setup(bot):
    await bot.add_cog(Give(bot))
