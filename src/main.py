import logging
import os

import discord
from discord.ext import commands
from dotenv import load_dotenv

load_dotenv()
discord_token = os.getenv("DISCORD_TOKEN")

handler = logging.FileHandler(filename="discord.log", encoding="utf-8", mode="w")
intents = discord.Intents.default()
intents.message_content = True
intents.members = True
intents.moderation = True


bot = commands.Bot(command_prefix="!", intents=intents, help_command=None)
