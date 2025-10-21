from discord.ext import commands
from pathlib import Path
from utils.database import Database
from utils.logger import get_logger
import discord
import sys

logger = get_logger()

class Bot(commands.Bot):
    def __init__(self):
        intents = discord.Intents.all()
        self.db = Database()
        super().__init__(command_prefix=commands.when_mentioned_or("!"), intents=intents)

    async def setup_hook(self):
        cogs_dir = Path(__file__).parent / "cogs"

        for path in cogs_dir.rglob("*.py"):
            if path.name.startswith("_"):
                continue

            module = (
                "cogs." 
                + str(path.relative_to(cogs_dir)).replace("/", ".").replace("\\", ".")[:-3]
            )

            try:
                await self.load_extension(module)
                logger.info(f"Loaded extension: {module}")
            except Exception as e:
                logger.info(f"Failed to load extension {module}. {e}")
                sys.exit()

        await self.tree.sync()
        logger.info("Slash commands synced.")
