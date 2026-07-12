from discord.ext import commands

from .help import Help


async def setup(client: commands.Bot) -> None:
    """ Tries to load the Cog to the client"""
    await client.add_cog(Help(client))

