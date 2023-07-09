#   greeter.py

from discord import client

# Commands and events for greeting users
class Greeter(commands.Cog):

    def __init__(self, client):
        self.client = client

    @commands.command()
    async def hello(self, ctx, *, member: discord.Member = None):
        """Says hello"""
        member = member or ctx.author
        await ctx.send(f"Hello, {member.name}")
