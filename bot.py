from discord.ext import commands
import random
bot = commands.Bot(command_prefix = "!")
@bot.command(name = "idea", help = "get a side project idea")
async def idea(ctx, help = "get a side project idea"):
    await ctx.send("Ideas are hard")
    await ctx.send("Worry not")
    topics = ['chat bot', 'cli', 'game', 'web bot', 'browser extension', 'api', 'web interface']
    area = ['note taking', 'social life', 'physical fitness', 'mental health', 'pet care']
    language = ['c++', 'python3', 'java', 'R']
    idea = f'Create a new {random.choice(topics)} by {random.choice(language)} that helps with {random.choice(area) }! :sunglasses:'
    await ctx.send(idea)

@bot.command(name = "calc", help = "Perform a calculation where fn is either -, +, *, /, %, or **")
async def calc(ctx, x: float, fn: str, y: float):
    if fn == '-':
        await ctx.send(x - y)
    elif fn == '+':
        await ctx.send(x + y)
    elif fn == '*':
        await ctx.send(x * y)
    elif fn == '/':
        await ctx.send(x / y)
    elif fn == "**":
        await ctx.send(x ** y)
    elif fn == '%':
        await ctx.send(x % y)
    else:
        await ctx.send("We are not currently supported that function, Please try again")
with open("BOT_TOKEN.txt", "r") as token_file:
    TOKEN = token_file.read()
    print("Token file read") 
    bot.run(TOKEN)
