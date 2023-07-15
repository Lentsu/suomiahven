#   greeter.py

from discord.ext import commands
import discord

# Commands and events for greeting users
class Greeter(commands.Cog):
    
    def __init__(self, client):
        self.client = client

    @commands.command()
    async def hello(self, ctx, member: discord.Member = None):
        """Says hello"""
        member = member or ctx.author
        await ctx.send(f"Hello, {member.display_name}!")

async def setup(client: commands.Bot) -> None:
    await client.add_cog(Greeter(client))
