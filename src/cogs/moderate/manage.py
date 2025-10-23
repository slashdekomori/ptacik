from discord.ext import commands


class Manage(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.db = bot.db


async def setup(bot):
    await bot.add_cog(Manage(bot))
