import os
from discord import Embed
from discord.ext import commands
from utils import http

RAPID_API_KEY = os.environ.get("WORDS_API_KEY")


class Fun(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="mean", aliases=["meaning"])
    async def meaning(self, ctx, *, word: str):
        """Meaning of a word"""
        response = await http.get(
            f"https://wordsapiv1.p.rapidapi.com/words/{word}",
            res_method="json",
            headers={
                "x-rapidapi-key": RAPID_API_KEY,
                "x-rapidapi-host": "wordsapiv1.p.rapidapi.com",
            },
        )
        if "results" not in response or response["results"] == []:
            return await ctx.send(
                embed=Embed(
                    description="Word have no meaning!",
                )
            )
        endl = "\n"
        result = response["results"][:5]
        display = []
        for i, w in enumerate(result):
            line = f"{i + 1}. (_{w['partOfSpeech']}_) {w['definition']}"
            if "examples" in w:
                line += endl + endl.join([f"• {e}" for e in w["examples"]])
            display.append(line)
        return await ctx.send(
            embed=Embed(
                title=word,
                description=f"/{response['pronunciation']['all']}/{endl}{endl.join(display)}",
            )
        )

    @commands.command(name="urban", aliases=["urbandict", "urbanmean"])
    async def urban(self, ctx, *, word: str):
        """Search Urban Dictionary for word meaning"""
        response = await http.get(
            f"https://api.urbandictionary.com/v0/define?term={word}",
            res_method="json",
        )
        if "list" not in response or response["list"] == []:
            return await ctx.send(
                embed=Embed(
                    description="Word have no meaning!",
                )
            )
        result = response["list"][:5]
        display = [
            f"{i + 1}. {word['definition']}\nExample: {word['example']}"
            for i, word in enumerate(result)
        ]
        return await ctx.send(embed=Embed(title=word, description="\n\n".join(display)))

    @commands.command(name="test")
    async def test(self, ctx, word: str):
        """Test command"""
        return await ctx.send("test")


def setup(bot):
    bot.add_cog(Fun(bot))
