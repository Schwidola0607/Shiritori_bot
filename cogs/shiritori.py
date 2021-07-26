from discord import Embed
from discord.ext import commands
from utils.enum import Mode, Dictionary, State
from utils.game import Game

DEFAULT_JOIN_EMOTE = "✅"


class Shiritori(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.shiritori_games = {}

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.content.startswith(self.bot.command_prefix):  # Ignore commands
            return await self.bot.process_commands(message)
        if (
            message.channel.id not in self.shiritori_games
        ):  # Ignore if no shiritori game is running
            return
        shiritori = self.shiritori_games[message.channel.id]
        if (
            shiritori.state != State.PLAYING and shiritori.state != State.LAST
        ):  # Ignore if not playing
            return
        if (
            shiritori.current_player
            and message.author.id != shiritori.current_player.id
        ):  # Ignore if not the current player
            return
        await shiritori.handle_word(message)

    @commands.Cog.listener()
    async def on_new_turn(self, message, current_letter):
        """
        New turn starts
        """
        shiritori = self.shiritori_games[message.channel.id]
        return await message.channel.send(
            content=f"<@!{shiritori.current_player.id}>",
            embed=Embed(
                title="Final turn! Answer a valid word to win!"
                if shiritori.state == State.LAST
                else "It's your turn!",
                description=f"Begin with the letter `{current_letter}`.\n"
                + f'{"{:.2f}".format(shiritori.get_time_left())} seconds left.',
            ),
        )

    @commands.Cog.listener()
    async def on_invalid_word(self, message):
        """
        Invalid answer
        """
        shiritori = self.shiritori_games[message.channel.id]
        return await message.reply(
            embed=Embed(
                title="Invalid word baka!",
                description=f"{shiritori.current_player.lives} ❤️ left\n"
                + "{:.2f}".format(shiritori.get_time_left())
                + " seconds left.\n"
            )
        )

    @commands.Cog.listener()
    async def on_no_time_left(self, message, current_player):
        """
        Player ran out of time
        """
        return await message.channel.send(
            content=f"<@!{current_player.id}>",
            embed=Embed(title="You ran out of time!"),
        )

    @commands.Cog.listener()
    async def on_no_lives_left(self, message, current_player):
        """
        Player ran out of lives
        """
        return await message.reply(
            content=f"<@!{current_player.id}>",
            embed=Embed(title="You ran out of ❤️!"),
        )

    @commands.Cog.listener()
    async def on_player_left(self, message, user):
        """
        Player left
        """
        return await message.channel.send(
            embed=Embed(title=f"<@!{user.id}> left the game")
        )

    @commands.Cog.listener()
    async def on_game_over(self, message, player = None):
        """
        Game over
        """
        return await message.channel.send(
            embed=Embed(
                title="Game ended!",
                description=f"Congratulations <@!{player.id}>!"
                if player is not None
                else f"Game ended in a draw!",
            )
        )

    @commands.Cog.listener()
    async def on_reaction_add(self, reaction, user):
        if (
            reaction.message.channel.id not in self.shiritori_games
        ):  # Ignore if no shiritori game is running
            return
        shiritori = self.shiritori_games[reaction.message.channel.id]
        if shiritori.state != State.READY:  # Ignore if not waiting for players
            return
        if (
            reaction.emoji != DEFAULT_JOIN_EMOTE
            or reaction.message.id != shiritori.start_message.id
        ):  # Ignore if not start message or wrong emote
            return
        if user.id == self.bot.user.id:  # Ignore if it's the bot
            return
        shiritori.add_player(user)
        print(f"{str(user)} joined game in channel {reaction.message.channel.name}")

    @commands.Cog.listener()
    async def on_reaction_remove(self, reaction, user):
        if (
            reaction.message.channel.id not in self.shiritori_games
        ):  # Ignore if no shiritori game is running
            return
        shiritori = self.shiritori_games[reaction.message.channel.id]
        if shiritori.state != State.READY:  # Ignore if not waiting for players
            return
        if (
            reaction.emoji != DEFAULT_JOIN_EMOTE
            or reaction.message.id != shiritori.start_message.id
        ):  # Ignore if not start message or wrong emote
            return
        shiritori.remove_player(user)
        print(f"{str(user)} left game in channel {reaction.message.channel.name}")

    @commands.group(name="shiritori", aliases=["s"])
    async def shiritori(self, ctx):
        """All shiritori commands"""
        if ctx.invoked_subcommand is None:
            await ctx.send_help(str(ctx.command))

    @shiritori.command(name="create", aliases=["c"])
    async def create_shiritori(
        self, ctx, mode: str = "bullet", dict: str = "english"
    ):
        f"""
        Create a shiritori game
        Game modes: {', '.join(list(map(lambda x: f'`{x}`', Mode.list())))}
        Dictionary types: {', '.join(list(map(lambda x: f'`{x}`', Dictionary.list())))}
        """
        if mode not in Mode:
            return await ctx.send(
                embed=Embed(
                    title=f"Invalid Game Mode",
                    description=f"The game modes are: {', '.join(list(map(lambda x: f'`{x}`', Mode.list())))}",
                )
            )
        if dict not in Dictionary:
            return await ctx.send(
                embed=Embed(
                    title=f"Invalid Dictionary Type",
                    description=f"The dictionary types are: {', '.join(list(map(lambda x: f'`{x}`', Dictionary.list())))}",
                )
            )
        if (
            ctx.channel.id in self.shiritori_games
            and self.shiritori_games[ctx.channel.id].state != State.IDLE
        ):
            return await ctx.send(
                embed=Embed(
                    title=f"A game is already in progress in this channel",
                    description=f"Please wait until the current game is finished before starting a new one",
                )
            )
        message = await ctx.send(
            embed=Embed(
                title=f"{ctx.message.author} is creating a new {mode.capitalize()} {Dictionary.to_str(dict)} game!",
                description=f"React with {DEFAULT_JOIN_EMOTE} to join the game.",
            )
        )
        await message.add_reaction(DEFAULT_JOIN_EMOTE)
        self.shiritori_games[ctx.channel.id] = Game(
            self.bot, message, ctx.message, mode, dict
        )

    @shiritori.command(name="start", aliases=["s"])
    async def start_shiritori(self, ctx):
        """Start a shiritori game"""
        if (
            ctx.channel.id not in self.shiritori_games
            or self.shiritori_games[ctx.channel.id].state == State.IDLE
        ):
            return await ctx.send(
                embed=Embed(
                    title=f"There is no game in progress in this channel",
                    description=f"Create a game with `{ctx.prefix}shiritori create`",
                )
            )

        shiritori = self.shiritori_games[ctx.channel.id]

        if shiritori.state != State.READY:
            return await ctx.send(
                embed=Embed(
                    title=f"A game is already in progress in this channel",
                    description=f"Please wait until the current game is finished before starting a new one",
                )
            )

        """
        if len(list(shiritori.players.keys())) < 2:
            return await ctx.send(
                embed=Embed(
                    title=f"Not enough players to start the game",
                    description=f"There must be at least 2 players in the game",
                )
            )
        """

        shiritori.start()
        await ctx.send(
            content=f"<@!{shiritori.current_player.id}>",
            embed=Embed(
                title=f"The game is starting!",
                description=f"Please choose a random {Dictionary.word(shiritori.dictionary)}",
            ),
        )

    @shiritori.command(name="abort", aliases=["end", "e"])
    async def abort_shiritori(self, ctx):
        """Abort the current shiritori game"""
        if (
            ctx.channel.id not in self.shiritori_games
            or self.shiritori_games[ctx.channel.id].state == State.IDLE
        ):
            return await ctx.send(
                embed=Embed(
                    title=f"There is no game in progress in this channel",
                    description=f"Create a game with `{ctx.prefix}shiritori create`",
                )
            )
        self.shiritori_games[ctx.channel.id].abort()

    @shiritori.command(name="resign", aliases=["r"])
    async def resign_shiritori(self, ctx):
        """Resign from the current shiritori game"""
        if (
            ctx.channel.id not in self.shiritori_games
            or self.shiritori_games[ctx.channel.id].state == State.IDLE
        ):
            return await ctx.send(
                embed=Embed(
                    title=f"There is no game in progress in this channel",
                    description=f"Create a game with `{ctx.prefix}shiritori create`",
                )
            )
        self.shiritori_games[ctx.channel.id].remove_player(ctx.author)

    @shiritori.command(name="leaderboard", aliases=["l"])
    async def leaderboard_shiritori(self, ctx):
        """Show the current leaderboard"""
        if (
            ctx.channel.id not in self.shiritori_games
            or self.shiritori_games[ctx.channel.id].state == State.READY
        ):
            return await ctx.send(
                embed=Embed(
                    title=f"There is no archived game in this channel yet",
                    description=f"Create a game with `{ctx.prefix}shiritori create` or start the current game.",
                )
            )
        shiritori = self.shiritori_games[ctx.channel.id]
        leaderboard = shiritori.leaderboard()
        display = []
        for i, player in enumerate(leaderboard):
            if player not in shiritori.in_game and (shiritori.state == State.PLAYING or shiritori.state == State.LAST):
                display.append(f"#{i + 1}: <@!{player.id}> [LEFT]")
            elif player.lives <= 0:
                display.append(f"#{i + 1}: <@!{player.id}> [OUT OF `❤️`]")
            elif player.time_left <= 0:
                display.append(f"#{i + 1}: <@!{player.id}> [OUT OF TIME]")
            else:
                display.append(
                    f"#{i + 1}: <@!{player.id}> [{f'{player.time_left:.2f} SECONDS LEFT' if shiritori.mode != Mode.SCRABBLE else f'{player.score} POINTS'}]"
                )
        await ctx.send(
            embed=Embed(
                title=f"{'Current' if shiritori.state != State.IDLE else 'Final'} Leaderboard",
                description="\n".join(display),
            )
        )


def setup(bot):
    bot.add_cog(Shiritori(bot))
