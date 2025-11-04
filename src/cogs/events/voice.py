import discord
from discord.ext import commands
import json
import os
from datetime import datetime, timezone
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv("TOKEN")
GUILD_ID = int(os.getenv("GUILD_ID"))

STATE_FILE = "data/vc_state.json"  # кто сейчас в войсе


class VoiceTracker(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.db = bot.db
        os.makedirs("data", exist_ok=True)
        if not os.path.exists(STATE_FILE):
            with open(STATE_FILE, "w") as f:
                json.dump({}, f)

    def load_state(self):
        with open(STATE_FILE, "r") as f:
            return json.load(f)

    def save_state(self, data):
        with open(STATE_FILE, "w") as f:
            json.dump(data, f, indent=4)

    @commands.Cog.listener()
    async def on_voice_state_update(self, member, before, after):
        now = datetime.now(timezone.utc).timestamp()
        state = self.load_state()
        uid = str(member.id)


        # === Пользователь ВОШЁЛ ===
        if before.channel is None and after.channel is not None:
            state[uid] = {
                "channel_id": after.channel.id,
                "join_time": now
            }
            self.save_state(state)

        # === Пользователь ВЫШЕЛ ===
        elif before.channel is not None and after.channel is None:
            session = state.pop(uid, None)

            if session:
                total_time = now - session["join_time"]
                await self.db.add_voice_time(member.id, total_time) 
                self.save_state(state)  # удаляем из активных

        # === Перешёл между каналами ===
        elif before.channel != after.channel:
            session = state.pop(uid, None)

            state[uid] = {
                "channel_id": after.channel.id,
                "join_time": session["join_time"] 
            }

            self.save_state(state)

async def setup(bot):
    await bot.add_cog(VoiceTracker(bot))
