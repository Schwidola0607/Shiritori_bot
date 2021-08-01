from discord import Embed
from discord import Member
from discord.ext import commands
import random

from utils.enum import Mode, Dictionary, State, Card
from utils.game import Game

DEFAULT_JOIN_EMOTE = "✅"
CTS = {'heal': 1, 'kill': 1, 'sub_time': 1, 'add_time': 1, 'poison': 3}
ROLL_SCORE = 20

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
    async def on_new_turn(self, message, current_letter=None, effect_message=None):
        """
        New turn starts
        """
        print(f'{effect_message} at shiritori')
        shiritori = self.shiritori_games[message.channel.id]
        if effect_message != "":
            await message.channel.send(
                embed=Embed(
                    title = f"{shiritori.current_player.name}, you have suffered from the following effects:",
                    description=f"{effect_message}"
                )
            )
        return await message.channel.send(
            content=f"<@!{shiritori.current_player.id}>",
            embed=Embed(
                title="Final turn! Answer a valid word to win!"
                if shiritori.state == State.LAST
                else "It's your turn!",
                description=f"Begin with the letter `{current_letter}`.\n{'{:.2f}'.format(shiritori.get_time_left())} seconds left."
                if current_letter is not None
                else f"Please choose a random {Dictionary.word(shiritori.dictionary)}",
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
                + " seconds left.\n",
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
    async def on_player_join(self, message, user):
        """
        Player join
        """
        print(f"{str(user)} joined game in channel {message.channel.name}")

    @commands.Cog.listener()
    async def on_player_left(self, message, user):
        """
        Player left
        """
        print(f"{str(user)} left game in channel {message.channel.name}")
        return await message.channel.send(
            embed=Embed(title=f"{user.name} left the game")
        )

    @commands.Cog.listener()
    async def on_game_over(self, message, player=None):
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

        current_author = reaction.message.embeds[0].title.split(' ')[0]
        current_player_list = [f'<@!{str(i)}>' for i in shiritori.players]
        await reaction.message.edit(
            embed=Embed(
                title=f"{current_author} is creating a new {shiritori.mode.capitalize()} {Dictionary.to_str(shiritori.dictionary)} game!",
                description=f"React with {DEFAULT_JOIN_EMOTE} to join the game.\n"
                    + f"Current players: {', '.join(current_player_list)}."
            )
        )

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
        
        current_author = reaction.message.embeds[0].title.split(' ')[0]
        current_player_list = [f'<@!{str(i)}>' for i in shiritori.players]
        await reaction.message.edit(
            embed=Embed(
                title=f"{current_author} is creating a new {shiritori.mode.capitalize()} {Dictionary.to_str(shiritori.dictionary)} game!",
                description=f"React with {DEFAULT_JOIN_EMOTE} to join the game.\n"
                    + f"Current players: {', '.join(current_player_list)}."
            )
        )

    @commands.group(name="shiritori", aliases=["s"])
    async def shiritori(self, ctx):
        """All shiritori commands"""
        if ctx.invoked_subcommand is None:
            await ctx.send_help(str(ctx.command))

    @shiritori.command(name="create", aliases=["c"])
    async def create_shiritori(self, ctx, mode: str = "bullet", dict: str = "english"):
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
                description=f"React with {DEFAULT_JOIN_EMOTE} to join the game.\n"
                + f"Current players: <@!{ctx.message.author.id}>",
            )
        )
        await message.add_reaction(DEFAULT_JOIN_EMOTE)
        self.shiritori_games[ctx.channel.id] = Game(
            self.bot, message, ctx.message, mode, dict
        )
        self.shiritori_games[ctx.channel.id].add_player(ctx.message.author)

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

        if len(list(shiritori.players.keys())) < 2:
            return await ctx.send(
                embed=Embed(
                    title=f"Not enough players to start the game",
                    description=f"There must be at least 2 players in the game",
                )
            )

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
        return await ctx.send(
            embed=Embed(
                title=f"Aborted current game",
            )
        )

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
        if ctx.channel.id not in self.shiritori_games:
            return await ctx.send(
                embed=Embed(
                    title=f"There is no archived game in this channel yet",
                    description=f"Create a game with `{ctx.prefix}shiritori create`.",
                )
            )
        shiritori = self.shiritori_games[ctx.channel.id]
        leaderboard = shiritori.leaderboard()
        display = []
        for i, player in enumerate(leaderboard):
            cur = f"[**#{i + 1}**] <@!{player.id}>"
            if player.id not in shiritori.in_game and (
                shiritori.state == State.PLAYING or shiritori.state == State.LAST
            ):
                cur += " [LEFT]"
            elif player.lives <= 0:
                cur += " [OUT OF `❤️`]"
            elif player.time_left <= 0:
                cur += " [OUT OF TIME]"
            else:
                cur += f" [{f'{player.time_left:.2f} SECONDS LEFT' if shiritori.mode != Mode.SCRABBLE else f'{player.score} POINTS'}]"
            display.append(cur)
        await ctx.send(
            embed=Embed(
                title=f"{'Current' if shiritori.state != State.IDLE else 'Final'} Leaderboard",
                description="\n".join(display),
            )
        )

    @shiritori.command(name="toggle_card_mode", aliases=["tcm"])
    async def toggle_card_shiritori(self, ctx):
        """Toggle card mode"""
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

        self.shiritori_games[ctx.channel.id].card_mode ^= 1
        str_mode = "on" if self.shiritori_games[ctx.channel.id].card_mode else "off"
        return await ctx.send(
            embed=Embed(
                title=f"Card mode turned {str_mode}",
            )
        )

    @shiritori.command(name="check_inventory", aliases=["ci"])
    async def check_inventory_shiritori(self, ctx):
        """(Card mode) Check your current inventory"""
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

        if self.shiritori_games[ctx.channel.id].card_mode != 1:
            return await ctx.send(
                embed=Embed(
                    title=f"Card mode not turned on yet!",
                    description=f"Use the toggle_card_mode command to turn on card mode before starting.",
                )
            )

        await ctx.send(
            embed=Embed(
                title=f"Your current inventory:",
                description=f"{', '.join(self.shiritori_games[ctx.channel.id].players[ctx.author.id].inventory)}",
            )
        )

    @shiritori.command(name="use_card", aliases=["uc"])
    async def use_card_shiritori(self, ctx, card: str = None, targeted_user: Member = None):
        """(Card mode) Use a card on a player in the game"""
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

        if self.shiritori_games[ctx.channel.id].card_mode != 1:
            return await ctx.send(
                embed=Embed(
                    title=f"Card mode not turned on yet!",
                    description=f"Use the toggle_card_mode command to turn on card mode before starting.",
                )
            )
        
        if (
            ctx.author.id != self.shiritori_games[ctx.channel.id].current_player.id
        ):
            return await ctx.send(
                embed=Embed(
                    title=f"Not your turn yet!",
                    description=f"Please wait until your turn to use the card.",
                )
            )

        if len(self.shiritori_games[ctx.channel.id].players[ctx.author.id].inventory) == 0:
            return await ctx.send(
                embed=Embed(
                    title=f"Empty inventory!",
                )
            )

        if card == None or card not in self.shiritori_games[ctx.channel.id].current_player.inventory:
            await ctx.send(
                embed=Embed(
                    title=f"Your current inventory:",
                    description=f"{', '.join(self.shiritori_games[ctx.channel.id].players[ctx.author.id].inventory)}",
                )
            )
            return await ctx.send(
                embed=Embed(
                    title=f"Invalid card!",
                    description=f"Please choose a card from one of the above.",
                )
            )
        if targeted_user == None or targeted_user.id not in self.shiritori_games[ctx.channel.id].in_game:
            await ctx.send(
                embed=Embed(
                    title=f"Your current inventory:",
                    description=f"{', '.join(self.shiritori_games[ctx.channel.id].players[ctx.author.id].inventory)}",
                )
            )
            return await ctx.send(
                embed=Embed(
                    title=f"Invalid targeted player!",
                    description=f"Please choose an player currently in the game.",
                )
            )
        self.shiritori_games[ctx.channel.id].use_card(ctx.author, card, targeted_user)
        await ctx.send(
            embed=Embed(
                description=f"{Card.word(card, CTS[card], targeted_user.id)}",
            )
        )

    # @shiritori.command(name="add_card", aliases=["ac"])
    # async def add_card_shiritori(self, ctx, card: str = None):
    #     if (
    #         ctx.channel.id not in self.shiritori_games
    #         or self.shiritori_games[ctx.channel.id].state == State.IDLE
    #     ):
    #         return await ctx.send(
    #             embed=Embed(
    #                 title=f"There is no game in progress in this channel",
    #                 description=f"Create a game with `{ctx.prefix}shiritori create`",
    #             )
    #         )

    #     if card == None:
    #         return await ctx.send(
    #             embed=Embed(
    #                 description=f"Please choose a card!",
    #             )
    #         )
    #     if card not in Card:
    #         return await ctx.send(
    #             embed=Embed(
    #                 title=f"Invalid card",
    #                 description=f"The cards are: {', '.join(list(map(lambda x: f'`{x}`', Card.list())))}",
    #             )
    #         )
    #     self.shiritori_games[ctx.channel.id].players[ctx.author.id].inventory.append(card)
    #     return await ctx.send(
    #         embed=Embed(
    #             description=f'{card} has been added into your inventory'
    #         )
    #     )

    @shiritori.command(name="roll_card", aliases=["rc"])
    async def roll_card_shiritori(self, ctx):
        """(Card mode) Roll a card using your points"""
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

        if self.shiritori_games[ctx.channel.id].card_mode != 1:
            return await ctx.send(
                embed=Embed(
                    title=f"Card mode not turned on yet!",
                    description=f"Use the toggle_card_mode command to turn on card mode before starting.",
                )
            )

        shiritori = self.shiritori_games[ctx.channel.id]

        if shiritori.mode != Mode.SCRABBLE:
            return await ctx.send(
                embed=Embed(
                    title=f"Invalid mode!",
                    description=f"This command is currently available in scrabble mode only",
                )
            )

        if ROLL_SCORE > shiritori.players[ctx.author.id].score:
            return await ctx.send(
                embed=Embed(
                    title=f"You don't have enough points yet!",
                    description=f"Each roll for cards will cost 10 points.",
                )
            )
        shiritori.players[ctx.author.id].score -= ROLL_SCORE

        card = random.choices(
            population=Card.list(),
            weights= (Card.get_rarity(crd) for crd in Card.list()),
            k=1)[0]

        shiritori.players[ctx.author.id].inventory.append(card)
        return await ctx.send(
            embed=Embed(
                title=f'You have received a {card} card.',
                description=f'{shiritori.players[ctx.author.id].score} points left.',
            )
        )
      
def setup(bot):
    bot.add_cog(Shiritori(bot))
