from discord.ext import commands


async def setup_error_handlers(bot):
    """Set up error handlers for bot commands"""

    @bot.event
    async def on_command_error(ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            # Get the command's help text
            if ctx.command.help:
                await ctx.send(
                    f"Missing required argument: {error.param.name}\n\nUsage: !{ctx.command.name} {ctx.command.signature}\n\n{ctx.command.help}"
                )
            else:
                await ctx.send(
                    f"Missing required argument: {error.param.name}\n\nUsage: !{ctx.command.name} {ctx.command.signature}"
                )
        elif isinstance(error, commands.MemberNotFound):
            await ctx.send("Member not found. Please mention a valid member.")
        elif isinstance(error, commands.BadArgument):
            await ctx.send(f"Invalid argument: {str(error)}")
        else:
            # Let other errors propagate to default handlers
            print(f"Unhandled error: {str(error)}")
