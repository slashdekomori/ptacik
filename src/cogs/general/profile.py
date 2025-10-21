import discord
from discord import app_commands, Interaction, User
from discord.ext import commands

devs = [749001740170559570,456802396874735616,1218993322442490036,1108543819370205255]

class General(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.db = bot.db

    @app_commands.command(name="profile", description="Узнать информацию о себе или о ком то.")
    @app_commands.describe(user="Пользователь о котором хотите посмотреть информацию.")
    async def profile(self, interaction: discord.Interaction, user: discord.User = None):
        target = user or interaction.user

        if target.bot:
            await interaction.response.send_message("Нельзя смотреть профиль ботов.", ephemeral=True)
            return

        await interaction.response.defer(thinking=True)

        worker = await self.db.get_workers(str(target.id))
        penalty = worker["penalty"]
        work_time = max(int(worker["work_time"]) - int(worker["break_time"]),0) / 3600

        embed = discord.Embed(
            title=f"Профиль {target.name}",
            description=f"Информация о пользователе",
            color=discord.Color.blurple()
        )

        embed.set_thumbnail(url=target.display_avatar.url)
        embed.add_field(name="Штрафы:", value=f"```{int(penalty)}```", inline=True)
        embed.add_field(name="Часов работы:", value=f"```{int(work_time)}```", inline=True)

        await interaction.followup.send(embed=embed)
    

async def setup(bot):
    await bot.add_cog(General(bot))