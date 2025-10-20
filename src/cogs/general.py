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
    
    @app_commands.command(name="give_penalty", description="Выдать штраф.")
    @app_commands.describe(user="Пользователь, которому хотите выдать штраф.")
    async def give_penalty(self, interaction: Interaction, user: User):
        if user.bot:
            await interaction.response.send_message("Нельзя дать пенальти боту", ephemeral=True)
            return

        if interaction.user.id not in devs:
            await interaction.response.send_message("У вас нет прав на использование этой команды.", ephemeral=True)
            return

        embed = discord.Embed(
            title=f"Штраф !",
            description=f"**Выдан пользователю {user.mention}**",
            color=discord.Color.dark_red()
        )

        await self.db.give_penalty(str(user.id))
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="forgive_penalty", description="Простить штраф.")
    @app_commands.describe(user="Пользователь, которому хотите простить штраф.")
    async def forgive_penalty(self, interaction: Interaction, user: User):

        if user.bot:
            await interaction.response.send_message("Нельзя простить пенальти боту", ephemeral=True)
            return

        if interaction.user.id not in devs:
            await interaction.response.send_message("У вас нет прав на использование этой команды.", ephemeral=True)
            return

        embed = discord.Embed(
            title=f"Штраф снят!",
            description=f"**У пользователя {user.mention}**",
            color=discord.Color.green()
        )

        await self.db.forgive_penalty_handle(str(user.id))
        await interaction.response.send_message(embed=embed)       

async def setup(bot):
    await bot.add_cog(General(bot))