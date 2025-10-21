import discord
from discord import app_commands, Interaction, User
from discord.ext import commands

class Manage(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.db = bot.db

async def setup(bot):
    await bot.add_cog(Manage(bot))