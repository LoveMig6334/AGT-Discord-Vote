import asyncio
import datetime
import logging
import os
from datetime import timedelta
from pathlib import Path

import discord
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


vote_sessions = {}


@bot.command()
async def vtimeout(ctx, member: discord.Member, duration: int):
    """
    Vote to timeout a member for a specified duration

    Parameters:
    - member: The member to timeout
    - timeout_min: The timeout duration in minutes (default: 5)
    """
    guild_id = ctx.guild.id
    target_id = member.id

    if guild_id not in vote_sessions:
        vote_sessions[guild_id] = {}

    # Avoid multiple votes on same member
    if target_id in vote_sessions[guild_id]:
        await ctx.send(f"A vote to timeout {member.mention} is already in progress.")
        return

    vote_sessions[guild_id][target_id] = {
        "voters": {ctx.author.id},
        "ends_at": datetime.utcnow() + timedelta(minutes=2),
    }
    await ctx.send(
        f"Vote started to timeout {member.mention}. React with ✅ to vote. Need 3 votes!"
    )

    msg = await ctx.send(f"React here to vote timeout for {member.mention}")
    await msg.add_reaction("✅")

    def check(reaction, user):
        return (
            reaction.message.id == msg.id
            and str(reaction.emoji) == "✅"
            and user.id != member.id
            and not user.bot
        )

    try:
        while datetime.utcnow() < vote_sessions[guild_id][target_id]["ends_at"]:
            reaction, user = await bot.wait_for(
                "reaction_add", timeout=120, check=check
            )
            vote_sessions[guild_id][target_id]["voters"].add(user.id)

            if len(vote_sessions[guild_id][target_id]["voters"]) >= 3:
                duration_sec = duration * 60
                await ctx.send(
                    f"{member.mention} has been timed out for {duration} minutes!"
                )
                await member.timeout(
                    discord.utils.utcnow() + timedelta(seconds=duration_sec)
                )
                del vote_sessions[guild_id][target_id]
                return
    except asyncio.TimeoutError:
        pass

    await ctx.send(f"Vote to timeout {member.mention} failed or expired.")
    del vote_sessions[guild_id][target_id]


bot.run(discord_token, log_handler=handler, log_level=logging.DEBUG)
