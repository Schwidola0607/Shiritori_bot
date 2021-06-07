import discord
from PyDictionary import PyDictionary
from discord import message
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

class Players:
    name = ""
    score = 0
    invalid_left = 3
    time_left = 10
    timer_state = 0
    timer = threading.Timer
    start_time = 0
    def __init__(self, name: str):
        self.name = name
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
        current_player = Players(str(ctx.message.author))
        shiritori.add_new_players(current_player)
        await ctx.send(f'{ctx.message.author} has joined the game')
    #print(f'debug checkpoint#2 {shiritori.state}')

#start the game
@bot.command(name = 'start')
async def start(ctx):
    if shiritori.state == 1:
        if shiritori.get_player_list_size() > 1:
            await ctx.send("Game is beginning")
            shiritori.start_game()
        else:
            await ctx.send("Not enough player!")
        # print(f'debug checkpoint#3 {shiritori.state}')
    else:
        await ctx.send("No current game")

@bot.event
async def on_message(message):
    channel = message.channel
    word = str(message.content)
    #print(f'reactional debug {shiritori.state}')
    if shiritori.state == 2 and str(message.author) == shiritori.current_turn_Player().name:
        shiritori.current_turn_Player().stop_countdown()
        # print(shiritori.current_turn_Player().time_left)
        if (shiritori.current_turn_Player().time_left < 0):
            await channel.send(f'You have ran out of time retard')
            await channel.send(str(shiritori.current_turn_Player().name) + " has been kicced.")
            shiritori.kick(shiritori.current_turn_Player())
            shiritori.next_turn()
            if (shiritori.check_end()):
                await channel.send(f'Game ended!')
                await channel.send(f'Congratulation {shiritori.get_winner().name}')
                shiritori.end()
                return

        if shiritori.check_word_validity(word) == 0:
            await channel.send(f'Invalid word Baka! " + {"{:.2f}".format(shiritori.current_turn_Player().time_left)} + " seconds left.')
            shiritori.current_turn_Player().invalid_left -= 1
            if shiritori.current_turn_Player().invalid_left < 0:
                await channel.send("Your word is invalid for more than 3 times retard")
                await channel.send(str(shiritori.current_turn_Player().name) + " has been kicced.")
                
                shiritori.current_turn_Player().stop_countdown()
                shiritori.kick(shiritori.current_turn_Player()) 
                shiritori.next_turn()
                
            if shiritori.check_end():
                await channel.send(f'Game ended!')
                await channel.send(f'Congratulation {shiritori.get_winner().name}')
                shiritori.end()
                return

        else:
            shiritori.add_new_word(word)
            shiritori.next_turn()
            await channel.send(f'{shiritori.current_turn_Player().name} your turn. ' + str(shiritori.current_turn_Player().time_left) + " seconds left.")

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