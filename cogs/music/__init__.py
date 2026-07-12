from discord.ext import commands

from .music import Music


async def setup(client: commands.Bot) -> None:
    """ Tries to load the Cog to the client"""
    await client.add_cog(Music(client))

