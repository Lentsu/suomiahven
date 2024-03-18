#   help.py

import discord
from discord import app_commands
from discord.ext import commands

# Import auxillary functions 
from cogs.auxillary import try_wrap

# Create the Help Cog to be loaded
class Help(commands.Cog):

    def __init__(self, client) -> None:
        self.client = client

    @app_commands.command(name="help")
    async def help(self, interaction: discord.Interaction) -> None:
        """ Displays a table of bot commands """
        # Create an embed of the title 
        em = discord.Embed(title="Commands", description="Here's a list of my bot commands.", color=discord.Color.blue())

        # Cycle through all commands 
        for command in self.client.tree.walk_commands():
            # Add the command to the embed
            em.add_field (
                name=f"/{command.name}", 
                value=command.description if command.description else command.name,
                inline=False
            )

        # Send the embed as a reponse to interaction
        await interaction.response.send_message(embed=em, ephemeral=True)

@try_wrap
async def setup(client: commands.Bot) -> None:
    await client.add_cog(Help(client))

