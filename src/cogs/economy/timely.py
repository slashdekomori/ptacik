import discord
from discord import app_commands, Interaction, User
from discord.ext import commands

from datetime import datetime, timedelta, timezone

class Timely(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.db = bot.db

    @app_commands.command(name="timely", description="Ежедневная награда.")
    async def profile(self, interaction: discord.Interaction):
        await interaction.response.defer(thinking=True)

        dbUser = await self.db.get_user(interaction.user.id)
        last_claimed = dbUser['last_claimed']

        now = datetime.now()
        unix_next = int((now + timedelta(hours=12)).timestamp())

        if now - last_claimed >= timedelta(hours=12):
            # Give reward
            await self.db.plus_balance(interaction.user.id, 50)
            await self.db.last_claimed(interaction.user.id, now)
            desc = f"{interaction.user.mention}, Вы забрали свои 50 монет. Возвращайтесь <t:{unix_next}:R>"
        else:
            desc = f"{interaction.user.mention}, Вы уже забрали свою временную награду! Возвращайтесь <t:{unix_next}:R>"
        

        embed = discord.Embed(
            title=f"Временная награда",
            description=desc,
            color=discord.Color.blurple()
        )
        embed.set_thumbnail(url=interaction.user.display_avatar.url)

        await interaction.followup.send(embed=embed)
        
async def setup(bot):
    await bot.add_cog(Timely(bot))