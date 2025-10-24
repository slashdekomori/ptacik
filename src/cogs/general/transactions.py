import discord
from discord import app_commands
from discord.ext import commands

from datetime import datetime

class PagedEmbedView(discord.ui.View):
    def __init__(self, pages: list[discord.Embed]):
        super().__init__(timeout=None)
        self.pages = pages
        self.index = 0
        self.update_buttons()

    def update_buttons(self):
        self.previous.disabled = self.index == 0
        self.next.disabled = self.index == len(self.pages) - 1

    @discord.ui.button(label="Назад", style=discord.ButtonStyle.gray)
    async def previous(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.index -= 1
        self.update_buttons()
        await interaction.response.edit_message(embed=self.pages[self.index], view=self)

    @discord.ui.button(label="Вперёд", style=discord.ButtonStyle.gray)
    async def next(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.index += 1
        self.update_buttons()
        await interaction.response.edit_message(embed=self.pages[self.index], view=self)


class Transactions(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.db = bot.db

    @app_commands.command(
        name="transactions", description="Посмотреть транзакции."
    )
    @app_commands.describe(user="Пользователь, транзакции которого хотите посмотреть.")
    async def profile(self, interaction: discord.Interaction, user: discord.User = None):
        await interaction.response.defer(thinking=True)
        target = user or interaction.user

        if target.bot:
            await interaction.followup.send("Нельзя смотреть транзакции ботов.", ephemeral=True)
            return

        # Загружаем транзакции из БД
        transactions = await self.db.get_transactions(target.id)

        if not transactions:
            await interaction.followup.send("У этого пользователя нет транзакций.")
            return

        # Создаём страницы по 5 записей
        per_page = 5
        pages = []
        for i in range(0, len(transactions), per_page):
            chunk = transactions[i:i + per_page]
            embed = discord.Embed(
                title=f"Транзакции {target.name} — стр. {i // per_page + 1}",
                color=discord.Color.blurple(),
            )
            for t in chunk:
                embed.add_field(
                    name=f"{t.get('description', 'Без описания')} — {t.get('quantity', 0)}",
                    value=f"{'➕' if t.get('type') == 1 else '➖'} • Дата: <t:{(int(t.get('datetime').timestamp()))}:R>",
                    inline=False,
                )
            pages.append(embed)

        # Отправляем первую страницу с кнопками
        view = PagedEmbedView(pages)
        await interaction.followup.send(embed=pages[0], view=view)


async def setup(bot):
    await bot.add_cog(Transactions(bot))
