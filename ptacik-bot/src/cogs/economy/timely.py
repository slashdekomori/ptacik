import discord
from discord import app_commands
from discord.ext import commands

from datetime import datetime, timedelta, timezone

import os
from dotenv import load_dotenv

load_dotenv()
GUILD_ID = os.getenv("GUILD_ID")


class Timely(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.db = bot.db

    @app_commands.guilds(discord.Object(id=int(GUILD_ID)))
    @app_commands.command(name="timely", description="Ежедневная награда.")
    async def profile(self, interaction: discord.Interaction):
        await interaction.response.defer(thinking=True)

        dbUser = await self.db.get_user(interaction.user.id)
        last_claimed = dbUser["last_claimed"]

        # UTC
        now = datetime.now(timezone.utc)
        next_claim = last_claimed + timedelta(hours=12)
        unix_next = int(next_claim.timestamp())

        if now >= next_claim:
            await self.db.plus_balance(interaction.user.id, 50, "Ежедневная награда")
            await self.db.last_claimed(interaction.user.id, now)
            next_claim = now + timedelta(hours=12)
            unix_next = int(next_claim.timestamp())
            desc = f"{interaction.user.mention}, Вы забрали свои 50 монет. Возвращайтесь <t:{unix_next}:R>"
        else:
            desc = f"{interaction.user.mention}, Вы уже забрали свою временную награду! Возвращайтесь <t:{unix_next}:R>"

        embed = discord.Embed(
            title="Временная награда",
            description=desc,
            color=discord.Color.from_str("#494949"),
        )
        embed.set_thumbnail(url=interaction.user.display_avatar.url)

        await interaction.followup.send(embed=embed)


async def setup(bot):
    await bot.add_cog(Timely(bot))
