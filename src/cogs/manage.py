import discord
from discord import app_commands, Interaction, User
from discord.ext import commands

# для парсинга времени 
import humanfriendly

from datetime import datetime, timezone
from zoneinfo import ZoneInfo

class Manage(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.db = bot.db

    @app_commands.command(name="start_work", description="Используй чтобы начать работу.")
    async def start_work(self, interaction: Interaction):
        start_work_time = datetime.now(ZoneInfo('Europe/Moscow'))
        start_work_time_str = start_work_time.astimezone().strftime("%H:%M")

        embed = discord.Embed(
            title="Работа начата!",
            description=f"{interaction.user.mention} начал работу.",
            color=discord.Color.blurple()
        )

        view = discord.ui.View(timeout=None)
        button = discord.ui.Button(label="Закончить работу", style=discord.ButtonStyle.primary)

        async def button_callback(btn_inter: Interaction):
            if btn_inter.user.id != interaction.user.id:
                return

            end_work_time = datetime.now(ZoneInfo("Europe/Moscow"))
            end_work_time_str = end_work_time.astimezone().strftime("%H:%M")

            time_worked_seconds = int((end_work_time - start_work_time).total_seconds())
            await self.db.start_work_handle(str(interaction.user.id), time_worked_seconds)

            button.disabled = True 
            view.clear_items()

            new_embed = discord.Embed(
                title="Работа окончена",
                description=(f"{interaction.user.name} закончил работу! \nСмена {start_work_time_str} - {end_work_time_str}"),
            )

            await btn_inter.response.edit_message(embed=new_embed, view=None) 

        button.callback = button_callback
        view.add_item(button)

        await interaction.response.send_message(embed=embed, view=view)

    @app_commands.command(name="take_break", description="Используй чтобы взять перерыв.")
    async def take_break(self, interaction: Interaction, time: str):
        parsed = humanfriendly.parse_timespan(time)

        embed = discord.Embed(
            title="Перерыв.",
            description=f"{interaction.user.mention} взял перерыв на {parsed} s",
            color=discord.Color.yellow()
        )

        await self.db.break_handle(str(interaction.user.id), parsed)
        await interaction.response.send_message(embed=embed)
 
async def setup(bot):
    await bot.add_cog(Manage(bot))