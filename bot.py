import discord
from PyDictionary import PyDictionary
from discord import message
from discord.ext import commands
import os
from dotenv import load_dotenv
import random
import time
load_dotenv()
intents = discord.Intents.all()
Dictionary = PyDictionary()
TOKEN = os.getenv('DISCORD_TOKEN')
GUILD = os.getenv('DISCORD_GUILD')
default_time = 120
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

class Countdown_timer:
    t = 0 #t - units second
    state = 0 #0 - stop running, 1 - currently counting down
    def __init__(self, t: int):
        self.t = t
        self.state = 0
    def begin(self):
        self.state = 1
    def stop(self):
        self.state = 0
    def count_down(self):
        while self.t >= 0 and self.state == 1:
            time.sleep(1)
            self.t -= 1 

class Players:
    name = ""
    score = 0
    clock = Countdown_timer()
    def __init__(self, name: str, t: int):
        self.name = name
        self.score = 0
        self.clock = Countdown_timer(t)
    def add_score(self, word: str):
        self.score += get_score(word)  
    def get_score(self) -> int:
        return self.score 

class Game:
    state = 0 #0 - not begin, 1 - waiting for players, 2 - start/on progress
    list_of_players = []
    list_of_used_words = []
    current_letter = ""
    position = 0
    def __init__(self):
        self.state = 0
        self.list_of_players = []
        self.list_of_used_words = []
        self.current_letter = ""
        self.position = 0
    def add_new_players(self, a: Players):
        self.list_of_players.append(a)
    def add_new_word(self, word: str):
        self.list_of_used_words.append(word)
        self.current_letter = word[len(word) - 1]
    def start_game(self):
        shiritori.state = 2
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
    def get_player_list_size(self) -> int:
        return len(self.list_of_players)
    def next_turn(self):
        self.position = self.position + 1
        if self.position == self.get_player_list_size():
            self.position = 0
    def current_turn_Player(self):
        return self.list_of_players[self.position]
    def end(self):
        self.state = 0
        self.list_of_players = []
        self.list_of_used_words = []
        self.current_letter = ""
        self.position = 0
shiritori = Game()

bot = commands.Bot(command_prefix = '&', intents = intents)
#play shiritori, create a new game
@bot.command(name = 'play')
async def play(ctx):
    shiritori.state = 1
    await ctx.send("Waiting for players to join")
    # print(f'debug checkpoint#1 {shiritori.state}')

#join the game    
@bot.command(name = 'join')
async def join(ctx):
    if shiritori.state == 2:
        await ctx.send("Game in progress!")
    elif shiritori.state == 0:
        await ctx.send("No current game")
    else:   
        current_player = Players(str(ctx.message.author), default_time)
        shiritori.add_new_players(current_player)
        await ctx.send(f'{ctx.message.author} has joined the game')
    # print(f'debug checkpoint#2 {shiritori.state}')

#start the game
@bot.command(name = 'start')
async def start(ctx):
    await ctx.send("Game is beginning")
    shiritori.start_game()
    # print(f'debug checkpoint#3 {shiritori.state}')

@bot.event
async def on_message(message):
    channel = message.channel
    word = str(message.content)
    if shiritori.state == 2:
        p = shiritori.current_turn_Player() 
        if str(message.author) == p.name:
        # print("input taken!")
            if shiritori.check_word_validity(word) == 0:
                await channel.send("Invalid word Baka!")
            else:
                p.add_score(word)
                p.clock.stop()
                shiritori.add_new_word(word)
                shiritori.next_turn()
                await channel.send(f'{p.name} your turn')
                p = shiritori.current_turn_Player()
                p.clock.begin()
                p.clock.count_down()           
    else:
        await bot.process_commands(message)

@bot.command(name = 'mean', help = "return the meaning of a string")
async def mean(ctx, word: str, word_type):
    temporary_dict = Dictionary.meaning(word)
    for s in temporary_dict[word_type]:
        await ctx.send(f'-{s}')
@bot.command(name = 'pick', help = "choose something")
async def pick(ctx, s:str):
    activity = s.split('/')
    print(activity)
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