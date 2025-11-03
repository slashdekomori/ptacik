from discord.ext import commands
import time
import asyncio  # 🔹 нужно для sleep
import random


last_typing = {}
COOLDOWN = 10
CHANCE = 30


class Typing(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.db = getattr(bot, "db", None)  # если у бота есть база данных

    @commands.Cog.listener()
    async def on_typing(self, channel, user, when):
        if user.bot:
            return

        now = time.time()
        user_id = user.id

        if user_id not in last_typing or now - last_typing[user_id] > COOLDOWN:
            last_typing[user_id] = now

            if random.random() <= (CHANCE / 100):
                msg = await channel.send(f"{user.mention} не пиши далбаёб")
                await asyncio.sleep(5)
                await msg.delete()


async def setup(bot):
    await bot.add_cog(Typing(bot))
