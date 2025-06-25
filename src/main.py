import logging
import os
from pathlib import Path

from discord.ext import commands
from dotenv import load_dotenv

from utils.load_intents import load_intents

load_dotenv()
discord_token = os.getenv("DISCORD_TOKEN")


logs_dir = Path(__file__).parent.parent / "logs"
logs_dir.mkdir(exist_ok=True)
print(f"Logging to {logs_dir / 'discord.log'}")

handler = logging.FileHandler(
    filename=logs_dir / "discord.log", encoding="utf-8", mode="w"
)
intents = load_intents()


bot = commands.Bot(command_prefix="!", intents=intents, help_command=None)


@bot.event
async def on_ready() -> None:
    print(f"Logged in as {bot.user.name} (ID: {bot.user.id})")


bot.run(discord_token, log_handler=handler, log_level=logging.DEBUG)
