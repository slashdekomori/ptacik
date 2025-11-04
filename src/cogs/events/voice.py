import discord
from discord.ext import commands
from datetime import datetime, timezone

STATE = {}

class VoiceTracker(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.db = bot.db

    def start_session(self, uid, now, muted=False):
        STATE[uid] = {
            "session_start_time": now,
            "muted": muted
        }

    async def end_session(self, uid, now):
        session = STATE.pop(uid, None)
        if session:
            total_time = now - session["session_start_time"]
            if session["muted"]:
                await self.db.add_muted_voice_time(uid, total_time)
            else:
                await self.db.add_voice_time(uid, total_time)

    @commands.Cog.listener()
    async def on_voice_state_update(self, member, before, after):
        now = datetime.now(timezone.utc)
        uid = member.id

        # === User joins a voice channel ===
        if before.channel is None and after.channel is not None:
            self.start_session(uid, now, after.self_mute)

        # === User leaves a voice channel ===
        elif before.channel is not None and after.channel is None:
            await self.end_session(uid, now)

        # === User toggles mute ===
        elif before.channel == after.channel and before.self_mute != after.self_mute:
            await self.end_session(uid, now)
            self.start_session(uid, now, after.self_mute)
            print(f"{member} {'muted' if after.self_mute else 'unmuted'}")


async def setup(bot):
    await bot.add_cog(VoiceTracker(bot))