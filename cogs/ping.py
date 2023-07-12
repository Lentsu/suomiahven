#   ping.py

import discord
from discord.ext import commands

# Commands and events for testing bot's latency
class Ping(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.command()
    async def ping(self, ctx):
        latency = round(self.client.latency * 1000)  # Calculate bot's latency in milliseconds
        await ctx.send(f"Pong! Letency: {latency} ms")

def setup(client):
    client.add_cog(Ping(client))
