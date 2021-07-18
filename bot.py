from discord.embeds import Embed
from fifa.check_fifa import check_players_name
import os
import discord
import requests
import json
from players import Players
from game import Game
from PyDictionary import PyDictionary
from discord.ext import commands
from dotenv import load_dotenv

load_dotenv()
intents = discord.Intents.all()
Dictionary = PyDictionary()
TOKEN = os.getenv('DISCORD_TOKEN')
COLOR = 0x00ff00

DEFAULT_TIME = 180
DEFAULT_DICT_TYPE = 0 
""" 0 for english, 1 for urban dictionary, 2 for MAL, 3 for fifa"""

shiritori = Game(DEFAULT_DICT_TYPE)
bot = commands.Bot(command_prefix = '&', intents = intents)

@bot.command(name = 'create', help = "Create a ultrabullet, bullet, blitz or srabble, shiritori game with different dictionary modes", aliases = ['c'])
async def create(ctx, game_type: str = None, dictionary_type: str = None):
    """create a game by selecting the game mode"""
    correct_game_type = True
    correct_dict_type = True
    global DEFAULT_TIME
    if game_type == "ultrabullet":
        DEFAULT_TIME = 30
    elif game_type == "bullet":
        DEFAULT_TIME = 60
    elif game_type == "blitz":
        DEFAULT_TIME = 180  
    elif game_type == "scrabble":
        shiritori.BOOL_SCRABBLE = True
    elif game_type == None:
        embed_var = discord.Embed(
            title = f'{ctx.message.author} please select a game mode!', 
            description = "ultrabullet, bullet, blitz, or scrabble", 
            color = COLOR
        )
        await ctx.message.channel.send(embed = embed_var)
        correct_game_type = False
    else:
        embed_var = discord.Embed(
            title = f'Invalid game mode. {ctx.message.author} please select again!', 
            description = "ultrabullet, bullet, blitz or scrabble", 
            color = COLOR
        )
        await ctx.message.channel.send(embed = embed_var)
        correct_game_type = False

    dict_index = -1
    if dictionary_type == "normal":
        dict_index = 0
    elif dictionary_type == "urbandict":
        dict_index = 1
    elif dictionary_type == "MAL":
        dict_index = 2
    elif dictionary_type == "fifa":
        dict_index = 3
    elif dictionary_type == None:
        embed_var = discord.Embed(
            title = f'{ctx.message.author} please select a dictionary mode!', 
            description = "normal, urbandict, MAL, or Fifa", 
            color = COLOR
        )
        await ctx.message.channel.send(embed = embed_var)
        correct_dict_type = False
    else:
        embed_var = discord.Embed(
            title = f'Invalid dictionary mode. {ctx.message.author} please select again!', 
            description = "normal, urbandict, MAL, or fifa", 
            color = COLOR
        )
        await ctx.message.channel.send(embed = embed_var)
        correct_dict_type = False

    if game_type == None or dictionary_type == None:
        return
    if correct_game_type == False or correct_dict_type == False:
        return
    shiritori.dict_type = dict_index
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

   
@bot.command(name = 'join', help = 'join a game', aliases = ['j'])
async def join(ctx):
    """join the current game"""
    if shiritori.state == 2:
        embed_var = discord.Embed(
            description = "Game in progress!", 
            color = COLOR
        )
        await ctx.message.channel.send(embed = embed_var)
    elif shiritori.state == 0 or shiritori.state == 3:
        embed_var = discord.Embed(
            description = "No current game.", 
            color = COLOR
        )
        await ctx.message.channel.send(embed = embed_var)
    else: 
        current_player = Players(str(ctx.message.author), DEFAULT_TIME)
        if shiritori.find_player(str(ctx.message.author)) != False:
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


@bot.command(name = 'start', help = 'start a game', aliases = ['s'])
async def start(ctx):
    """start the current game"""
    # print(shiritori.dict_type)
    if shiritori.state == 1:
        if shiritori.get_player_list_size() > 1:
            shiritori.start_game()
            desc = f'The game is beginning. {shiritori.current_turn_Player().name} '
            if shiritori.dict_type == 0:
                desc = desc + 'Please choose a random English word.'
            elif shiritori.dict_type == 1:
                desc = desc + 'Please choose a random Urban Dictionary phrase.'
            elif shiritori.dict_type == 2:
                desc = desc + 'Please choose the full name of a random anime character.'
            elif shiritori.dict_type == 3:
                desc = desc + 'Please choose a fifa player name.'
            embed_var = discord.Embed(
                description = desc, 
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
    if shiritori.state == 2 and str(message.author) == shiritori.current_turn_Player().name and message.content[0] != '&':
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
                    + "{:.2f}".format(shiritori.current_turn_Player().time_left)
                    + ' seconds left.\n', 
                    color = COLOR
                )
                await channel.send(embed = embed_var)
                if shiritori.BOOL_SCRABBLE == True:
                    shiritori.current_turn_Player().penalty(20)
                    embed_var = discord.Embed(
                        description = '-20 points penalty',
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

@bot.command(name = 'resign', help = "resign from the game", aliases = ['r'])
async def resign(ctx):
    """abort the game"""
    player_name = str(ctx.message.author)
    if shiritori.state == 1:
        in_the_game = 0
        for s in shiritori.list_of_players:
            if player_name == s.name:
                shiritori.kick(s)
                in_the_game = 1
        if in_the_game:
            embed_var = discord.Embed(
            description = f"{player_name} has resigned from the game.", 
            color = COLOR)
            await ctx.message.channel.send(embed = embed_var)
        else:
            embed_var = discord.Embed(
            description = f"{player_name} You are not in the game yet!", 
            color = COLOR)
            await ctx.message.channel.send(embed = embed_var)


    elif shiritori.state == 2:
        nxt_turn = 0
        if  player_name == shiritori.current_turn_Player().name:
            nxt_turn = 1
        for s in shiritori.list_of_players:
            if player_name == s.name:
                shiritori.kick(s)
                s.out_of_rank()
        embed_var = discord.Embed(
            description = f"{player_name} has resigned from the game.", 
            color = COLOR)
        await ctx.message.channel.send(embed = embed_var)

        if nxt_turn:
            shiritori.next_turn()

        if shiritori.check_end():
            embed_var = discord.Embed(
                title = "Game ended!", 
                description = f'Congratulations {shiritori.get_winner().name}', 
                color = COLOR)
            await ctx.channel.send(embed = embed_var)
            shiritori.end()
            return

        embed_var = discord.Embed(
        description = f'{shiritori.current_turn_Player().name} your turn.' +
        f'{"{:.2f}".format(shiritori.current_turn_Player().time_left)} seconds left.', 
        color = COLOR
        )
        await ctx.channel.send(embed = embed_var)

    else:
        embed_var = discord.Embed(
            description = "No current game.", 
            color = COLOR
        )
        await ctx.message.channel.send(embed = embed_var)

@bot.command(name = 'kicc', help = "kicc a player", aliases = ['k'])
async def kicc(ctx, player_name: str):
    """abort the game"""
    if shiritori.state == 1:
        in_the_game = 0
        for s in shiritori.list_of_players:
            if player_name == s.name:
                shiritori.kick(s)
                in_the_game = 1
        print(in_the_game)

        if in_the_game:
            embed_var = discord.Embed(
            description = f"{player_name} has been kicked from the game.", 
            color = COLOR)
            await ctx.message.channel.send(embed = embed_var)
        else:
            embed_var = discord.Embed(
            description = f"{player_name} is not in the game yet!", 
            color = COLOR)
            await ctx.message.channel.send(embed = embed_var)

    elif shiritori.state == 2:
        if str(ctx.message.author) != shiritori.game_owner().name:
            embed_var = discord.Embed(
                description=f'{ctx.message.author}' 
                ' you do not have permission', 
                color = COLOR
            )
            await ctx.message.channel.send(embed = embed_var)
        else:
            nxt_turn = 0
            has_find = False
            if  player_name == shiritori.current_turn_Player().name:
                nxt_turn = 1
            for s in shiritori.list_of_players:
                if player_name == s.name:
                    has_find = True
                    shiritori.kick(s)
                    s.out_of_rank()
            if has_find == True:
                embed_var = discord.Embed(
                    description = f"{player_name} has been kicced from the game.", 
                    color = COLOR)
                await ctx.message.channel.send(embed = embed_var)
            else:
                embed_var = discord.Embed(
                    description = f'{player_name} is not in the game yet!',
                    color = COLOR
                )
                await ctx.message.channel.send(embed = embed_var)
            if nxt_turn:
                shiritori.next_turn()

            if shiritori.check_end():
                embed_var = discord.Embed(
                    title = "Game ended!", 
                    description = f'Congratulations {shiritori.get_winner().name}', 
                    color = COLOR)
                await ctx.channel.send(embed = embed_var)
                shiritori.end()
                return

            embed_var = discord.Embed(
            description = f'{shiritori.current_turn_Player().name} your turn.' +
            f'{"{:.2f}".format(shiritori.current_turn_Player().time_left)} seconds left.', 
            color = COLOR
            )
            await ctx.channel.send(embed = embed_var)

    else:
        embed_var = discord.Embed(
            description = "No current game.", 
            color = COLOR
        )
        await ctx.message.channel.send(embed = embed_var)

@bot.command(name = 'rank', help = "display leaderboard") 
async def rank(ctx):
    if shiritori.state == 3:
        ranking = shiritori.display_leaderboard()
        for i in ranking:
            print(f'{i.name} {i.score}')
        desc = ""
        print(len(ranking))
        for i in range (len(ranking)):
            desc = desc + f'#{i + 1}: {ranking[i].name} with {ranking[i].get_score()} points\n'
        embed_var = discord.Embed(
            title = 'Final leaderboard',
            description = desc,
            color = COLOR
        )
        await ctx.message.channel.send(embed = embed_var)
   
@bot.command(name = 'abort', help = "abort the game")
async def abort(ctx):
    """abort the game"""
    if shiritori.state == 1 or shiritori.state == 2:
        if str(ctx.message.author) != shiritori.game_owner().name:
            embed_var = discord.Embed(
                description=f'{ctx.message.author}' 
                ', you do not have permission', 
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

@bot.command(name = 'urbanmean', help = "return the meaning of a string in urban dictionary")
async def urbanmean(ctx, word: str):
    response = requests.get("https://api.urbandictionary.com/v0/define?term=" + word).text
    dict_response = json.loads(response)
    if ('error' in dict_response): # url is redirected
        new_url = requests.get("https://www.urbandictionary.com/define.php?term="+ word).url
        new_word = new_url.rsplit('term=', 1)[1] # get the word redirected to (after the 'term=' part in the url)
        word = new_word
        response = requests.get("https://api.urbandictionary.com/v0/define?term=" + word).text
        dict_response = json.loads(response)

    def_list = dict_response['list']
    if not len(def_list):
        embed_var = discord.Embed(
        description='The phrase has no meaning!', 
        color = COLOR
        )
        await ctx.send(embed = embed_var)
    else:
        for mean in def_list:
            embed_var = discord.Embed(
            description=str(mean['definition']), 
            color = COLOR
            )
            await ctx.send(embed = embed_var)
    
@bot.event
async def on_ready():
    print("On Board")

async def announce_kick():
    pass

bot.run(TOKEN)