import os
import discord
from utils.data import Bot
from dotenv import load_dotenv

load_dotenv()

bot = Bot(
    command_prefix="&",
    guild=os.environ.get("DISCORD_GUILD"),
    allowed_mentions=discord.AllowedMentions(everyone=False, roles=False),
    intents=discord.Intents(guilds=True, members=True, messages=True, reactions=True),
)

for file in os.listdir("cogs"):
    if file.endswith(".py"):
        bot.load_extension(f"cogs.{file[:-3]}")

try:
    bot.run(os.environ.get("DISCORD_TOKEN"))
except Exception as e:
    print(f"Error when logging in: {e}")
