import os
from discord import Embed
from discord.ext import commands
from utils import http

OXFORD_APP_ID = os.environ.get("OXFORD_APP_ID")
OXFORD_APP_KEY = os.environ.get("OXFORD_APP_KEY")


class Fun(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="mean", aliases=["meaning"])
    async def meaning(self, ctx, *, word: str):
        """Meaning of a word"""
        response = await http.get(
            f"https://od-api.oxforddictionaries.com/api/v2/entries/en-gb/{word}",
            res_method="json",
            headers={"app_id": OXFORD_APP_ID, "app_key": OXFORD_APP_KEY},
        )
        if "error" in response:
            return await ctx.send(
                embed=Embed(
                    description="Word have no meaning!",
                )
            )
        result = response["results"][0]["lexicalEntries"][0]
        type = result["lexicalCategory"]["id"]
        definitions = result["entries"][0]["senses"][:5]
        display = [
            f"{i + 1}. {word['definitions'][0]}" for i, word in enumerate(definitions)
        ]
        endl = "\n"
        return await ctx.send(
            embed=Embed(title=word, description=f"__{type}__{endl}{endl.join(display)}")
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
