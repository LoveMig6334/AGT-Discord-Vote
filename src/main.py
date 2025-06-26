import datetime
import logging
import os
from datetime import datetime, timedelta
from pathlib import Path

from discord.ext import commands
from dotenv import load_dotenv

from utils.command_error_handler import setup_error_handlers
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
    await setup_error_handlers(bot)


vote_sessions = {}


@bot.command()
async def vtimeout(ctx, member: commands.MemberConverter, timeout_min: int = 5):
    """
    Vote to timeout a member for a specified duration

    Parameters:
    - member: The member to timeout
    - timeout_min: The timeout duration in minutes (default: 5)
    """
    guild_id = ctx.guild.id
    member_id = member.id

    if guild_id not in vote_sessions:
        vote_sessions[guild_id] = {}

    if member_id in vote_sessions[guild_id]:
        await ctx.send(f"A vote to timeout {member.mention} is already in progress.")
        return

    vote_sessions[guild_id][member_id] = {
        "voters": {ctx.author.id},
        "ends_at": datetime.utcnow() + timedelta(minutes=2),
    }
    await ctx.send(
        f"Vote started to timeout {member.mention}. React with ✅ to vote. Need 3 votes!"
    )

    message = await ctx.send(f"React here to vote timeout for {member.mention}")

    await message.add_reaction("✅")

    def check(reaction, user):
        return (
            user == ctx.author
            and str(reaction.emoji) == "✅"
            and reaction.message.id == message.id
        )

    try:
        await bot.wait_for("reaction_add", timeout=60.0, check=check)
    except TimeoutError:
        await ctx.send("Vote timed out.")
    else:
        await ctx.send("Vote counted!")


bot.run(discord_token, log_handler=handler, log_level=logging.DEBUG)
