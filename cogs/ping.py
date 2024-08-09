#   ping.py

import discord
from discord import app_commands
from discord.ext import commands

# Import auxillary functions 
from cogs.auxillary import try_wrap

# Commands and events for testing bot's latency
class Ping(commands.Cog):

    def __init__(self, client) -> None:
        self.client = client

    @app_commands.command(name="ping")
    async def ping(self, interaction: discord.Interaction) -> None:
        """ Prints the bot's client latency in milliseconds. """
        latency = round(self.client.latency * 1000)  # Calculate bot's latency in milliseconds
        await interaction.response.send_message(f"Pong! Latency: {latency} ms", ephemeral=False)

@try_wrap
async def setup(client) -> None:
    await client.add_cog(Ping(client))
