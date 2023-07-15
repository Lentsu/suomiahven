#   help.py

import discord
from discord.ext import commands

class Help(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.command(name="ohje")
    async def help(self, ctx):
        embed = discord.Embed(title="Botin komennot", description="Tässä on lista saatavilla olevista komennoista", color=discord.Color.blue())

        # Lisää komennot embediin
        embed.add_field(name="!ping", value="Tarkista botin viive")
        embed.add_field(name="!hello", value="Toivota käyttäjälle 'Hello'")
        embed.add_field(name="!ohje", value="Näyttää tämän viestin")


        await ctx.send(embed=embed)

async def setup(client: commands.Bot) -> None:
    await client.add_cog(Help(client))
