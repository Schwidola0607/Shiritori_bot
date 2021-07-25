import traceback
from discord import activity
from discord.ext.commands import AutoShardedBot, errors


def traceback_maker(err, advance: bool = True):
    """A way to debug your code anywhere"""
    _traceback = "".join(traceback.format_tb(err.__traceback__))
    error = ("```py\n{1}{0}: {2}\n```").format(type(err).__name__, _traceback, err)
    return error if advance else f"{type(err).__name__}: {err}"


class Bot(AutoShardedBot):
    def __init__(self, *args, guild=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.guild = guild

    async def on_ready(self):
        print(f"Logged in as {self.user}")
        await self.change_presence(activity=activity.Game(name="with your mom"))

    async def on_message(self, message):
        if not self.is_ready() or message.author.bot or message.guild.id != self.guild:
            return

        await self.process_commands(message)

    async def on_command(self, ctx):
        print(f"{ctx.author} used command {ctx.command}")

    async def on_command_error(self, ctx, error):
        if isinstance(error, errors.MissingRequiredArgument) or isinstance(
            error, errors.BadArgument
        ):
            helper = (
                str(ctx.invoked_subcommand)
                if ctx.invoked_subcommand
                else str(ctx.command)
            )
            await ctx.send_help(helper)

        elif isinstance(error, errors.CommandInvokeError):
            err = traceback_maker(error.original)
            if "2000 or fewer" in str(error) and len(ctx.message.clean_content) > 1900:
                return await ctx.send(
                    "You attempted to make the command display more than 2,000 characters...\n"
                    "Both error and command will be ignored."
                )
            await ctx.send(f"An error occurred while processing the command:\n{err}")

        elif isinstance(error, errors.CheckFailure):
            pass

        elif isinstance(error, errors.MaxConcurrencyReached):
            await ctx.send(
                "You've reached max capacity of command usage at once. Please finish the previous one..."
            )

        elif isinstance(error, errors.CommandOnCooldown):
            await ctx.send(
                f"This command is on cooldown. Try again after {error.retry_after:.2f} seconds."
            )

        elif isinstance(error, errors.CommandNotFound):
            pass
