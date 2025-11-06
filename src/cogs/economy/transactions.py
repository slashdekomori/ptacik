import discord
from discord import app_commands
from discord.ext import commands


import os
from dotenv import load_dotenv
load_dotenv()
GUILD_ID = os.getenv("GUILD_ID")



class PagedEmbedView(discord.ui.View):
    def __init__(self, pages: list[discord.Embed]):
        super().__init__(timeout=180)
        self.pages = pages
        self.index = 0
        self.update_buttons()

    def update_buttons(self):
        self.previous.disabled = self.index == 0
        self.next.disabled = self.index == len(self.pages) - 1

    @discord.ui.button(label="Назад", style=discord.ButtonStyle.gray)
    async def previous(
        self, interaction: discord.Interaction, button: discord.ui.Button
    ):
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



    @app_commands.guilds(discord.Object(id=int(GUILD_ID)))
    @app_commands.command(name="transactions", description="Посмотреть транзакции.")
    @app_commands.describe(user="Пользователь, транзакции которого хотите посмотреть.")
    async def profile(
        self, interaction: discord.Interaction, user: discord.User = None
    ):
        await interaction.response.defer(thinking=True)
        target = user or interaction.user

        if target.bot:
            await interaction.followup.send(
                "Нельзя смотреть транзакции ботов.", ephemeral=True
            )
            return

        transactions = await self.db.get_transactions(target.id)

        if not transactions:
            await interaction.followup.send("У этого пользователя нет транзакций.")
            return

        avatar = interaction.user.display_avatar.url
        if user is not None:
            avatar = target.display_avatar.url

        per_page = 5
        pages = []
        for i in range(0, len(transactions), per_page):
            chunk = transactions[i : i + per_page]
            embed = discord.Embed(
                title=f"Транзакции — {target.name}",
                color=discord.Color.from_str("#494949"),
            )
            for t in chunk:
                dt = t.get("datetime")
                unix_ts = int(dt.timestamp())
                plusminus = "➕" if t.get("type") == 1 else "➖"
                quantity = t.get("quantity", 0)
                embed.add_field(
                    name=f"{plusminus} {quantity} [<t:{int(unix_ts)}:f>]",
                    value=f"{t.get('description')}",
                    inline=False,
                )
            pages.append(embed)
            embed.set_thumbnail(url=avatar)
            embed.set_footer(
                text=f"стр. {i // per_page + 1}/{round(len(transactions) / 5)}"
            )

        view = PagedEmbedView(pages)
        await interaction.followup.send(embed=pages[0], view=view)



async def setup(bot):
    await bot.add_cog(Transactions(bot))
