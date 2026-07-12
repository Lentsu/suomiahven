from discord.ext import commands

from .template import Template


async def setup(client: commands.Bot) -> None:
    """ Tries to load the Cog to the client"""
    await client.add_cog(Template(client))

