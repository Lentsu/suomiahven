#   greeter.py

from discord.ext import commands
from discord import app_commands
import discord

# Import auxillary methods
from cogs.aux import try_wrap

# Commands and events for greeting users
class Greeter(commands.Cog):

    def __init__(self, client) -> None:
        self.client = client

    @app_commands.command(name="hello")
    async def hello(self, interaction: discord.Interaction) -> None:
        """Says hello"""
        await interaction.response.send_message(f"Hello, {interaction.user.display_name}!", ephemeral=True)

@try_wrap
async def setup(client: commands.Bot) -> None:
    await client.add_cog(Greeter(client))
