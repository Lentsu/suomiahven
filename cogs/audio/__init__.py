from discord.ext import commands

from .audio import Audio 


async def setup(client: commands.Bot) -> None:
    """ Tries to load the Cog to the client"""
    await client.add_cog(Audio(client))

