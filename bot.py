import os
import time
import threading
import discord
from PyDictionary import PyDictionary
from discord.ext import commands
from dotenv import load_dotenv
load_dotenv()
intents = discord.Intents.all()
Dictionary = PyDictionary()
TOKEN = os.getenv('DISCORD_TOKEN')
GUILD = os.getenv('DISCORD_GUILD')
COLOR = 0x00ff00
scrabble_score = {"a": 1, "c": 3, "b": 3, "e": 1, "d": 2, "g": 2,
        "f": 4, "i": 1, "h": 4, "k": 5, "j": 8, "m": 3,
        "l": 1, "o": 1, "n": 1, "q": 10, "p": 3, "s": 1,
        "r": 1, "u": 1, "t": 1, "w": 4, "v": 4, "y": 4,
        "x": 8, "z": 10}
def get_score(word: str) -> int:
    """return the score of a word according to scrabble"""
    res = 0
    for letter in word:
        res += scrabble_score[letter]
    return res
DEFAULT_TIME = 1800
class Players:
    """ a class to represent players"""
    name = ""
    score = 0
    invalid_left = 3
    time_left = 0
    timer_state = 0
    timer = threading.Timer
    start_time = 0
    def __init__(self, name: str, t: int):
        self.name = name
        self.time_left = t
    def add_score(self, word: str):
        """add score to a Player"""
        self.score += get_score(word)  
    def get_score(self) -> int:
        """get score of a Player"""
        return self.score 
    def get_remaining_time(self) -> int: 
        """get remaining time of a player units: second"""
        return self.time_left
    def reduce_clock(self):
        """substract one second from a Player's remaining time"""
        self.time_left -= 1
    def countdown(self):
        """countdown"""
        self.timer = threading.Timer(self.time_left, self.reduce_clock)
        self.start_time = time.time()
        self.timer.start()
    def stop_countdown(self):
        """stop the countdown timer"""
        self.timer.cancel()
        self.time_left -= time.time() - self.start_time

class Game:
    """a class to represent the current instance of a game"""
    state = 0 #0 - not begin, 1 - waiting for players, 2 - start/on progress, 3 - has just ended
    list_of_players = []
    list_of_used_words = []
    leaderboard = []
    current_letter = ""
    position = 0
    def __init__(self):
        self.state = 0
        self.list_of_players = []
        self.list_of_used_words = []
        self.leaderboard = []
        self.current_letter = ""
        self.position = 0
    def add_new_players(self, gamer: Players):
        """add a new player when joined"""
        self.list_of_players.append(gamer)
    def add_new_word(self, word: str):
        """new word to list_of_used_word after a turn"""
        self.list_of_used_words.append(word)
        self.current_letter = word[len(word) - 1]
    def start_game(self):
        """method to start game"""
        self.state = 2
        self.current_turn_Player().countdown()
    def check_word_validity(self, word: str):
        """check for a word validitiy according to the Shiritori's rule"""
        if ' ' in word:
            return 0
        if any(not c.isalnum() for c in word):
            return 0
        if (self.current_letter != '' and word[0] != self.current_letter):
            return 0
        if word in self.list_of_used_words:
            return 0
        temporary_dict = Dictionary.meaning(word)
        return temporary_dict is not None
    def find_player(self, name: str) -> bool:
        for gamer in self.list_of_players:
            if gamer.name == name:
                return True
    def game_owner(self) -> Players:
        """return the game owner"""
        return self.list_of_players[0]
    def get_player_list_size(self) -> int:
        """return the current number of players"""
        return len(self.list_of_players)
    def current_turn_Player(self):
        """return this turn's Player"""
        return self.list_of_players[self.position]
    def kick(self, gamer: Players):
        """disqualify a player based on time, or the number of invalid times"""
        self.list_of_players.remove(gamer)
        self.position -= 1
    def next_turn(self):
        """move to next Player's turn"""
        self.position = self.position + 1
        if self.position == self.get_player_list_size():
            self.position = 0
        self.current_turn_Player().countdown()
    def check_end(self):
        """end game condition"""
        for gamer in self.list_of_players:
            if gamer.get_remaining_time() < 0:
                self.list_of_players.remove(gamer)
                self.leaderboard.append(gamer)
        return self.state == 2 and self.get_player_list_size() == 1
    def end(self):
        """method to end the game"""
        self.state = 3
        self.list_of_players = []
        self.list_of_used_words = []
        self.leaderboard = []
        self.current_letter = ""
        self.position = 0

    def get_winner(self) -> Players:
        """return the winner"""
        return self.list_of_players[0]

shiritori = Game()
bot = commands.Bot(command_prefix = '&', intents = intents)
@bot.command(name = 'create', help = "Create a blitz, bullet or casual shiritori game")
async def create(ctx, game_type: str = None):
    """create a game by selecting the game mode"""
    global DEFAULT_TIME
    if game_type == "bullet":
        DEFAULT_TIME = 60
    elif game_type == "blitz":
        DEFAULT_TIME = 180
    elif game_type == "casual":
        DEFAULT_TIME = 1800
    elif game_type == None:
        embed_var = discord.Embed(
            title = f'{ctx.message.author} please select a game mode!', 
            description = "bullet, blitz, or casual", 
            color = COLOR
        )
        await ctx.message.channel.send(embed = embed_var)
        return
    else:
        embed_var = discord.Embed(
            title = f'Invalid game mode. {ctx.message.author} please select again!', 
            description = "bullet, blitz, or casual", 
            color = COLOR
        )
        await ctx.message.channel.send(embed = embed_var)
        return
    shiritori.state = 1
    current_player = Players(str(ctx.message.author), DEFAULT_TIME)
    shiritori.add_new_players(current_player)
    embed_var = discord.Embed(
        title = f'{ctx.message.author} is creating a new game!', 
        description = "Type &join to join the game.", 
        color = COLOR
    )
    await ctx.message.channel.send(embed = embed_var)
    # print(f'debug checkpoint#1 {shiritori.state}')

   
@bot.command(name = 'join')
async def join(ctx):
    """join the current game"""
    if shiritori.state == 2:
        embed_var = discord.Embed(
            description = "Game in progress!", 
            color = COLOR
        )
        await ctx.message.channel.send(embed = embed_var)
    elif shiritori.state == 0:
        embed_var = discord.Embed(
            description = "No current game.", 
            color = COLOR
        )
        await ctx.message.channel.send(embed = embed_var)
    else: 
        print(DEFAULT_TIME) 
        current_player = Players(str(ctx.message.author), DEFAULT_TIME)
        if shiritori.find_player(str(ctx.message.author)):
            embed_var = discord.Embed(
                    description = f'{ctx.message.author}'
                    ' You are already in the game!', 
                    color = COLOR
            )
            await ctx.message.channel.send(embed = embed_var)
            return
        shiritori.add_new_players(current_player)
        embed_var = discord.Embed(
            description = f'{ctx.message.author}'
            ' has joined the game.', 
            color = COLOR
        )
        await ctx.message.channel.send(embed = embed_var)
    #print(f'debug checkpoint#2 {shiritori.state}')


@bot.command(name = 'start')
async def start(ctx):
    """start the current game"""
    if shiritori.state == 1:
        if shiritori.get_player_list_size() > 1:
            shiritori.start_game()  
            embed_var = discord.Embed(
                description = f'The game is beginning. {shiritori.current_turn_Player().name}' 
                ' Please choose a random English word.', 
                color = COLOR
            )
            await ctx.message.channel.send(embed = embed_var)
        else:
            embed_var = discord.Embed(
                description = "Not enough players!", 
                color = COLOR
            )
            await ctx.message.channel.send(embed = embed_var)
        # print(f'debug checkpoint#3 {shiritori.state}')
    else: 
        embed_var = discord.Embed(
            description = "No current game.", 
            color = COLOR
        )
        await ctx.message.channel.send(embed = embed_var)

@bot.event
async def on_message(message):
    """reaction to messages currently served mainly in the game Shiritori"""
    channel = message.channel
    word = str(message.content)
    #print(f'reactional debug {shiritori.state}')
    if shiritori.state == 2 and str(message.author) == shiritori.current_turn_Player().name:
        shiritori.current_turn_Player().stop_countdown()
        # print(shiritori.current_turn_Player().time_left)
        if shiritori.current_turn_Player().time_left < 0:
            embed_var = discord.Embed(
                description = f'{message.author}'
                '  You have ran out of time.', 
                color = COLOR
            )
            await channel.send(embed = embed_var)
            embed_var = discord.Embed(
                description = f'{message.author}'
                ' has been kicced from the game.', 
                color = COLOR)
            await channel.send(embed = embed_var)

            shiritori.kick(shiritori.current_turn_Player())
            shiritori.next_turn()

            if shiritori.check_end():
                embed_var = discord.Embed(
                    title = "Game ended!", 
                    description = f'Congratulation {shiritori.get_winner().name}', 
                    color = COLOR)
                await channel.send(embed = embed_var)
                shiritori.end()
                return

            embed_var = discord.Embed(
                description = f'{shiritori.current_turn_Player().name} your turn.' +
                f'{"{:.2f}".format(shiritori.current_turn_Player().time_left)} seconds left.', 
                color = COLOR)
            await channel.send(embed = embed_var)

        else:
            if shiritori.check_word_validity(word) == 0:
                shiritori.current_turn_Player().countdown()
                embed_var = discord.Embed(
                    description = 'Invalid word Baka! ' 
                    +"{:.2f}".format(shiritori.current_turn_Player().time_left)
                    +' seconds left.', 
                    color = COLOR
                )
                await channel.send(embed = embed_var)

                shiritori.current_turn_Player().invalid_left -= 1
                if shiritori.current_turn_Player().invalid_left < 0:
                    embed_var = discord.Embed(
                        description = f'{message.author}'
                        ' Your word is invalid for more than 3 times.', 
                        color = COLOR
                    )
                    await channel.send(embed = embed_var)
                    embed_var = discord.Embed(
                        description = f'{message.author}'
                        '  has been kicced from the game.', 
                        color = COLOR
                    ) 
                    await channel.send(embed = embed_var)
                    shiritori.kick(shiritori.current_turn_Player()) 
                    shiritori.next_turn()
                    embed_var = discord.Embed(
                    description = f'{shiritori.current_turn_Player().name} your turn.' +
                    f'{"{:.2f}".format(shiritori.current_turn_Player().time_left)} seconds left.', 
                    color = COLOR
                    )
                    await channel.send(embed = embed_var)
                    
                if shiritori.check_end():
                    embed_var = discord.Embed(
                        title = "Game ended!", 
                        description = f'Congratulation {shiritori.get_winner().name}', 
                        color = COLOR
                    )
                    await channel.send(embed = embed_var)
                    shiritori.end()
                    return

            else:
                shiritori.add_new_word(word)
                shiritori.next_turn()
                
                embed_var = discord.Embed(
                    description = f'{shiritori.current_turn_Player().name} your turn. ' +
                    f'{"{:.2f}".format(shiritori.current_turn_Player().time_left)} seconds left.', 
                    color = COLOR
                )
                await channel.send(embed = embed_var)

    else:
        await bot.process_commands(message)

@bot.command(name = 'abort', help = "abort the game")
async def abort(ctx):
    """abort the game"""
    if (shiritori.state == 1 or shiritori.state == 2):
        if str(ctx.message.author) != shiritori.game_owner().name:
            embed_var = discord.Embed(
                description=f'{ctx.message.author}' 
                'you do not have permission', 
                color = COLOR
            )
            await ctx.message.channel.send(embed = embed_var)
        else:
            shiritori.end()
            embed_var = discord.Embed(
                description = "The game has been aborted.", 
                color = COLOR)
            await ctx.message.channel.send(embed = embed_var)
    else:
        embed_var = discord.Embed(
            description = "No current game.", 
            color = COLOR
        )
        await ctx.message.channel.send(embed = embed_var)

@bot.command(name = 'mean', help = "return the meaning of a string")
async def mean(ctx, word: str, word_type):
    """return the meaning(s) of a word"""
    temporary_dict = Dictionary.meaning(word)
    for meaning_line in temporary_dict[word_type]:
        embed_var = discord.Embed(
            description=f'-{meaning_line}', 
            color = COLOR
        )
        await ctx.send(embed = embed_var)    
        
@bot.event
async def on_ready():
    """fucntion to confirm bot on board and
    print out existing members in the current guild"""        
    guild = discord.utils.find(lambda g: g.name == GUILD, bot.guilds)
    print(
        f'{bot.user} has connected to the following guild:\n'
        f'{guild.name}(id: {guild.id})'   
        )
    members ='\n - '.join([member.name for member in guild.members])
    print(f'Guild Members:\n -{members}')
bot.run(TOKEN)
