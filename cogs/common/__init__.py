from discord.ext import commands

from .common import Common 


async def setup(client: commands.Bot) -> None:
    """ Tries to load the Cog to the client"""
    await client.add_cog(Common(client))

