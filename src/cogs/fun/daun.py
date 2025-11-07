import discord
from discord import app_commands
from discord.ext import commands


import os
from dotenv import load_dotenv
load_dotenv()
GUILD_ID = os.getenv("GUILD_ID")

def daun_lang(s: str) -> str:
    mapping = {
        'ё': 'о',
        'й': 'и',
        'к': 'г',
        'п': 'б',
        'с': 'з',
        'т': 'д',
        'ф': 'в',
        'ш': 'ж',
        'и': 'е',
    }
    out_chars = []
    for ch in s:
        lower = ch.lower()

        if lower in mapping:
            repl = mapping[lower]
        else:
            repl = lower

        if ch.isupper():
            out_chars.append(repl.upper())
        else:
            out_chars.append(repl)

    return ''.join(out_chars)


class Daun(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.db = bot.db

    # @app_commands.guilds(discord.Object(id=int(GUILD_ID)))
    @app_commands.command(
        name="daun", description="Стань дауном."
    )
    @app_commands.describe(text="текст")
    async def daun(
        self, interaction: discord.Interaction, text: str 
    ):
        await interaction.response.defer(thinking=True)

        msg = daun_lang(text) 

        await interaction.followup.send(content=msg)
        


async def setup(bot):
    await bot.add_cog(Daun(bot))
