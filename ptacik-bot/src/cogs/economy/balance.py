import discord
from discord import app_commands
from discord.ext import commands


import os
from dotenv import load_dotenv

load_dotenv()
GUILD_ID = os.getenv("GUILD_ID")


class Balance(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.db = bot.db

    @app_commands.guilds(discord.Object(id=int(GUILD_ID)))
    @app_commands.command(name="balance", description="Посмотреть баланс")
    @app_commands.describe(user="Пользователь о котором хотите посмотреть информацию.")
    async def balance(
        self, interaction: discord.Interaction, user: discord.User = None
    ):
        await interaction.response.defer(thinking=True)

        target = user or interaction.user

        if target.bot:
            embed = discord.Embed(
                title=f"Баланс {target.name}",
                description="Нельзя смотреть баланс ботов",
                color=discord.Color.from_str("#494949"),
            )
            await interaction.followup.send_message(embed=embed, ephemeral=True)
            return

        user = await self.db.get_user(target.id)

        embed = discord.Embed(
            title=f"Баланс {target.name}",
            color=discord.Color.from_str("#494949"),
        )
        embed.set_thumbnail(url=target.display_avatar.url)
        embed.add_field(name="Монет", value=f"```{user['balance']}```", inline=True)

        await interaction.followup.send(embed=embed)


async def setup(bot):
    await bot.add_cog(Balance(bot))
