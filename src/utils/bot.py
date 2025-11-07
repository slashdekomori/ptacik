from discord.ext import commands
from pathlib import Path
from utils.database import Database
from utils.logger import get_logger
import discord
import sys
import os

logger = get_logger()


class Bot(commands.Bot):
    def __init__(self):
        intents = discord.Intents.all()
        self.db = Database()
        super().__init__(
            command_prefix=commands.when_mentioned_or("!"), intents=intents
        )

    async def setup_hook(self):
        src_dir = Path(__file__).parent.parent
        cogs_dir = src_dir / "cogs"

        sys.path.append(str(src_dir))  # ensure 'src' is in PYTHONPATH

        for path in cogs_dir.rglob("*.py"):
            if path.name.startswith("_"):
                continue

            relative_path = path.relative_to(src_dir)
            module = ".".join(
                relative_path.with_suffix("").parts
            )  # cogs.general.profile

            try:
                await self.load_extension(module)
                logger.info(f"Loaded extension: {module}")
            except Exception as e:
                logger.error(f"Failed to load extension {module}: {e}")
                sys.exit(1)

        await self.tree.sync()
        logger.info("Slash commands synced.")
