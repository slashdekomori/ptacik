from discord.ext import commands
from dotenv import load_dotenv

from utils.database import Database
from utils.logger import get_logger
from utils.bot import Bot

import os, sys, discord
from pathlib import Path

load_dotenv()
token = os.getenv("TOKEN")

bot = Bot()
bot.run(token)