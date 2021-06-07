import discord
from PyDictionary import PyDictionary
from discord import message
from discord import embeds
from discord.colour import Color
from discord.ext import commands
import os
from dotenv import load_dotenv
import random
import time
import threading
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
    res = 0
    for letter in word:
        res += scrabble_score[letter]
    return res
default_time = 1800
class Players:
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
        self.score += get_score(word)  
    def get_score(self) -> int:
        return self.score 
    def get_remaining_time(self) -> int: #unit: seconds
        return self.time_left
    def reduce_clock(self):
        self.time_left -= 1
    def countdown(self):
        self.timer = threading.Timer(self.time_left, self.reduce_clock)
        self.start_time = time.time()
        self.timer.start()
    def stop_countdown(self):
        self.timer.cancel()
        self.time_left -= time.time() - self.start_time

class Game:
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
    def add_new_players(self, a: Players):
        self.list_of_players.append(a)
    def add_new_word(self, word: str):
        self.list_of_used_words.append(word)
        self.current_letter = word[len(word) - 1]
    def start_game(self):
        self.state = 2
        self.current_turn_Player().countdown()
    def check_word_validity(self, word: str):
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
    def game_owner(self) -> Players:
        return self.list_of_players[0]
    def get_player_list_size(self) -> int:
        return len(self.list_of_players)
    def next_turn(self):
        self.position = self.position + 1
        if self.position == self.get_player_list_size():
            self.position = 0
        self.current_turn_Player().countdown()

    def current_turn_Player(self):
        return self.list_of_players[self.position]
    def end(self):
        self.state = 3
        self.list_of_players = []
        self.list_of_used_words = []
        self.leaderboard = []
        self.current_letter = ""
        self.position = 0
    def get_winner(self) -> Players:
        return self.list_of_players[0]
    def check_end(self):
        # for a in self.list_of_players:
        #      if a.get_remaining_time() < 0:
        #          self.list_of_players.remove(a)
        #          self.leaderboard.append(a)
        return self.state == 2 and self.get_player_list_size() == 1
    def kick(self, a: Players):
        self.list_of_players.remove(a)
        self.position -= 1
shiritori = Game()
bot = commands.Bot(command_prefix = '&', intents = intents)

#play shiritori, create a new game
@bot.command(name = 'play', help = "Create a blitz, bullet or casual shiritori game")
async def play(ctx, game_type: str):
    # print(game_type)
    global default_time
    if game_type == "bullet":
        default_time = 60
    elif game_type == "blitz":
        default_time = 180
    elif game_type == "casual":
        default_time = 1800
    else:
        embedVar = discord.Embed(title=f'{ctx.message.author} please select a game mode!', 
        description="bullet, blitz, or casual", color=COLOR)
        await ctx.message.channel.send(embed=embedVar)
        return
    shiritori.state = 1
    embedVar = discord.Embed(title=f'{ctx.message.author} is creating a new game!', description="Type &join to join the game.", color=COLOR)
    await ctx.message.channel.send(embed=embedVar)
    # print(f'debug checkpoint#1 {shiritori.state}')

#join the game    
@bot.command(name = 'join')
async def join(ctx):
    if shiritori.state == 2:
        embedVar = discord.Embed(description="Game in progress!", color=COLOR)
        await ctx.message.channel.send(embed=embedVar)
    elif shiritori.state == 0:
        embedVar = discord.Embed(description="No current game.", color=COLOR)
        await ctx.message.channel.send(embed=embedVar)
    else: 
        print(default_time) 
        current_player = Players(str(ctx.message.author), default_time)
        for a in shiritori.list_of_players:
            if str(ctx.message.author) == a.name:
                embedVar = discord.Embed(description=f'{ctx.message.author} You are already in the game!', color=COLOR)
                await ctx.message.channel.send(embed=embedVar)
                return
        shiritori.add_new_players(current_player)
        embedVar = discord.Embed(description= f'{ctx.message.author} has joined the game.', color=COLOR)
        await ctx.message.channel.send(embed=embedVar)
    #print(f'debug checkpoint#2 {shiritori.state}')

#start the game
@bot.command(name = 'start')
async def start(ctx):
    if shiritori.state == 1:
        if shiritori.get_player_list_size() > 1:
            shiritori.start_game()  
            embedVar = discord.Embed(description=f'The game is beginning. {shiritori.current_turn_Player().name} Please choose a random English word.', color=COLOR)
            await ctx.message.channel.send(embed=embedVar)
        else:
            embedVar = discord.Embed(description="Not enough players!", color=COLOR)
            await ctx.message.channel.send(embed=embedVar)
        # print(f'debug checkpoint#3 {shiritori.state}')
    else: 
        embedVar = discord.Embed(description="No current game.", color=COLOR)
        await ctx.message.channel.send(embed=embedVar)

@bot.event
async def on_message(message):
    channel = message.channel
    word = str(message.content)
    #print(f'reactional debug {shiritori.state}')
    if shiritori.state == 2 and str(message.author) == shiritori.current_turn_Player().name:
        shiritori.current_turn_Player().stop_countdown()
        # print(shiritori.current_turn_Player().time_left)
        if (shiritori.current_turn_Player().time_left < 0):
            embedVar = discord.Embed(description=f'{message.author}  You have ran out of time.', color=COLOR)
            await channel.send(embed=embedVar)
            embedVar = discord.Embed(description=f'{message.author} has been kicced from the game.', color=COLOR)
            await channel.send(embed=embedVar)

            shiritori.kick(shiritori.current_turn_Player())
            shiritori.next_turn()

            if (shiritori.check_end()):
                embedVar = discord.Embed(title = f'Game ended!', description = f'Congratulation {shiritori.get_winner().name}', color=COLOR)
                await channel.send(embed=embedVar)
                shiritori.end()
                return

        else:
            if shiritori.check_word_validity(word) == 0:
                embedVar = discord.Embed(description=f'Invalid word Baka! {"{:.2f}".format(shiritori.current_turn_Player().time_left)} seconds left.', color=COLOR)
                await channel.send(embed=embedVar)

                shiritori.current_turn_Player().invalid_left -= 1
                if shiritori.current_turn_Player().invalid_left < 0:
                    embedVar = discord.Embed(description=f'{message.author} Your word is invalid for more than 3 times.', color=COLOR)
                    await channel.send(embed=embedVar)
                    embedVar = discord.Embed(description=f'{message.author}  has been kicced from the game.', color=COLOR)
                    await channel.send(embed=embedVar)
                    shiritori.kick(shiritori.current_turn_Player()) 
                    shiritori.next_turn()
                    
                if (shiritori.check_end()):
                    embedVar = discord.Embed(title = f'Game ended!', description=f'Congratulation {shiritori.get_winner().name}', color=COLOR)
                    await channel.send(embed=embedVar)
                    shiritori.end()
                    return

            else:
                shiritori.add_new_word(word)
                shiritori.next_turn()
                
                embedVar = discord.Embed(description=f'{shiritori.current_turn_Player().name} your turn. {"{:.2f}".format(shiritori.current_turn_Player().time_left)} seconds left.', color=COLOR)
                await channel.send(embed=embedVar)

    else:
        await bot.process_commands(message)

@bot.command(name = 'abort', help = "abort the game")
async def abort(ctx):
    if (shiritori.state == 1 or shiritori.state == 2):
        if(str(ctx.message.author) != shiritori.game_owner().name):
            embedVar = discord.Embed(description=f'{ctx.message.author} you do not have permission', color=COLOR)
            await ctx.message.channel.send(embed=embedVar)
        else:
            shiritori.end()
            embedVar = discord.Embed(description="The game has been aborted.", color=COLOR)
            await ctx.message.channel.send(embed=embedVar)
    else:
        embedVar = discord.Embed(description="No current game.", color=COLOR)
        await ctx.message.channel.send(embed=embedVar)

@bot.command(name = 'mean', help = "return the meaning of a string")
async def mean(ctx, word: str, word_type):
    temporary_dict = Dictionary.meaning(word)
    for s in temporary_dict[word_type]:
        await ctx.send(f'-{s}')
    
@bot.command(name = 'pick', help = "choose something")
async def pick(ctx, s:str):
    activity = s.split('/')
    # print(activity)
    if len(activity) >= 1:
        await ctx.send(f'{bot.user} chooses :point_right:{random.choice(activity)}:point_left:')
    else:
        await ctx.send(f'{bot.user} chooses :point_right:{random.choice(["YES", "NO"])}:point_left:')
@bot.event
async def on_ready():        
    guild = discord.utils.find(lambda g: g.name == GUILD, bot.guilds)
    print(
        f'{bot.user} has connected to the following guild:\n'
        f'{guild.name}(id: {guild.id})'   
        )
    members ='\n - '.join([member.name for member in guild.members])
    print(f'Guild Members:\n -{members}')


bot.run(TOKEN)