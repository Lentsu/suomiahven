#   template.py

from discord.ext import commands
from discord import app_commands
import discord

# Import local auxillary functions
from cogs.auxillary import try_wrap

# Commands and events for greeting users
class Template(commands.Cog):

    def __init__(self, client) -> None:
        self.client = client

    @app_commands.command(name="test")
    async def command(self, interaction: discord.Interaction) -> None:
        """ Command description for the autogenerated help function """
        await interaction.response.send_message("Interaction response", ephemeral=False)

@try_wrap
async def setup(client: commands.Bot) -> None:
    """ Tries to load the Cog to the client and prints [OK] on success """
    await client.add_cog(Template(client))

