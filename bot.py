import discord
from PyDictionary import PyDictionary
from discord.ext import commands
import os
from dotenv import load_dotenv
load_dotenv()
intents = discord.Intents.all()
Dictionary = PyDictionary()
TOKEN = os.getenv('DISCORD_TOKEN')
GUILD = os.getenv('DISCORD_GUILD')

bot = commands.Bot(command_prefix = "&", intents = intents)
@bot.command(name = 'test')
async def test(ctx):
    guild = discord.utils.find(lambda g: g.name == GUILD, bot.guilds)
    if(ctx.message.author == guild.owner):
        await ctx.send("Baka!!")

@bot.command(name = 'mean', help = "return the meaning of a string")
async def get_mean(ctx, word: str, word_type):
    temporary_dict = Dictionary.meaning(word)
    for s in temporary_dict[word_type]:
        await ctx.send(f'-{s}')

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