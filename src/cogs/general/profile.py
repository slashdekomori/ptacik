import discord
from discord import app_commands
from discord.ext import commands


devs = [
    749001740170559570,
    456802396874735616,
    1218993322442490036,
    1108543819370205255,
]


class General(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.db = bot.db

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
            color=discord.Color.blurple(),
        )

        embed.set_thumbnail(url=target.display_avatar.url)
        embed.add_field(name="Монет", value=f"```{user['balance']}```", inline=True)
        embed.add_field(
            name="Часов:", value=f"```{user['voice_time'] // 3600}```", inline=True
        )

        await interaction.followup.send(embed=embed)


async def setup(bot):
    await bot.add_cog(General(bot))
