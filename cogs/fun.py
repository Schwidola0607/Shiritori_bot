import os
from discord import Embed
from discord.ext import commands
from utils import http

<<<<<<< HEAD
OXFORD_APP_ID = os.environ.get("OXFORD_APP_ID")
OXFORD_APP_KEY = os.environ.get("OXFORD_APP_KEY")
=======
RAPID_API_KEY = os.environ.get("WORDS_API_KEY")
>>>>>>> e4d80e090b45cb3c5cdb0996a4e0f20e92b21f09


class Fun(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="mean", aliases=["meaning"])
    async def meaning(self, ctx, *, word: str):
        """Meaning of a word"""
        response = await http.get(
<<<<<<< HEAD
            f"https://od-api.oxforddictionaries.com/api/v2/entries/en-gb/{word}",
            res_method="json",
            headers={"app_id": OXFORD_APP_ID, "app_key": OXFORD_APP_KEY},
        )
        if "error" in response:
=======
            f"https://wordsapiv1.p.rapidapi.com/words/{word}",
            res_method="json",
            headers={
                "x-rapidapi-key": RAPID_API_KEY,
                "x-rapidapi-host": "wordsapiv1.p.rapidapi.com",
            },
        )
        if "results" not in response or response["results"] == []:
>>>>>>> e4d80e090b45cb3c5cdb0996a4e0f20e92b21f09
            return await ctx.send(
                embed=Embed(
                    description="Word have no meaning!",
                )
            )
<<<<<<< HEAD
        result = response["results"][0]["lexicalEntries"][0]
        type = result["lexicalCategory"]["id"]
        definitions = result["entries"][0]["senses"][:5]
        display = [
            f"{i + 1}. {word['definitions'][0]}" for i, word in enumerate(definitions)
        ]
        endl = "\n"
        return await ctx.send(
            embed=Embed(title=word, description=f"__{type}__{endl}{endl.join(display)}")
=======
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
>>>>>>> e4d80e090b45cb3c5cdb0996a4e0f20e92b21f09
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
