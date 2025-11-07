import discord
from discord import app_commands
from discord.ext import commands


import os
from dotenv import load_dotenv

load_dotenv()
GUILD_ID = os.getenv("GUILD_ID")


def format_short_time(seconds: int) -> str:
    hours = seconds // 3600
    minutes = (seconds % 3600) // 60

    parts = []
    if hours:
        parts.append(f"{hours} ч")
    if minutes or not parts:
        parts.append(f"{minutes} мин")

    return " ".join(parts)


class Profile(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.db = bot.db

    @app_commands.guilds(discord.Object(id=int(GUILD_ID)))
    @app_commands.command(
        name="profile", description="Узнать информацию о себе или о ком то."
    )
    @app_commands.describe(user="Пользователь о котором хотите посмотреть информацию.")
    async def profile(
        self, interaction: discord.Interaction, user: discord.User = None
    ):
        await interaction.response.defer(thinking=True)
        target = user or interaction.user

        if target.bot:
            await interaction.followup.send_message(
                "Нельзя смотреть профиль ботов.", ephemeral=True
            )
            return

        user = await self.db.get_user(target.id)

        embed = discord.Embed(
            title=f"Профиль {target.name}",
            description="Информация о пользователе",
            color=discord.Color.from_str("#494949"),
        )

        voice_time = format_short_time(user["voice_time"])
        muted_time = format_short_time(user["muted_time"])
        balance = user["balance"]

        embed.set_thumbnail(url=target.display_avatar.url)
        embed.add_field(name=" ·  Монет", value=f"```{balance:^29}```", inline=False)
        embed.add_field(name=" ·  Говоря", value=f"```{voice_time}```", inline=True)
        embed.add_field(name=" ·  Молча", value=f"```{muted_time}```", inline=True)
        embed.add_field(
            name=" ·  Сообщений", value=f"```{user['message_count']}```", inline=True
        )
        await interaction.followup.send(embed=embed)


async def setup(bot):
    await bot.add_cog(Profile(bot))
