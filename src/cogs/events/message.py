import discord
from discord.ext import commands
from datetime import datetime, timezone
from utils.logger import get_logger
import os
from dotenv import load_dotenv

load_dotenv()
GUILD_ID = os.getenv("GUILD_ID")
logger = get_logger()


class MessageTracker(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.db = bot.db



    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if message.guild is None:
            return
        if message.guild.id != int(GUILD_ID):
            return
        if message.author.bot:
            return
        await self.db.add_message(message.author.id)        
        logger.debug(f"[{message.channel.name}] {message.author.name}: {message.content}")


async def setup(bot):
    await bot.add_cog(MessageTracker(bot))
