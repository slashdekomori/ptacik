from dotenv import load_dotenv

from utils.bot import Bot

import os

load_dotenv()
token = os.getenv("TOKEN")

bot = Bot()
bot.run(token)
