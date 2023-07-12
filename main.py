#   main.py
import os                       # For shell

# BEGIN HEADER

""" A Discord bot written for the private Discord server Perch of Finland"""

__author__      = "Lenni Toikkanen"
__copyright__   = "Free to use"

# END
    
# Import libraries
import random                       # For randomizing stuff
import discord                      # For Discord abstractions
from discord.ext import commands    # For load_extension and other stuff
from dotenv import load_dotenv      # For local Tokens

# Custom class that extends commands.Bot with serverside functionality and cogs list
class Client(commands.Bot):

    # Init client 
    def __init__(self):
        super().__init__(command_prefix=commands.when_mentioned_or('!'), intents=discord.Intents.all())

        self.cogs_list = [
            "greeter"
            "ping"
        ]

    # Load all 'Cogs' as client extensions
    async def setup_hook(self):
        for cog in self.cogs_list:
            await client.load_extension(f"cogs.{cog}")

    # When connection is made
    async def on_ready(self):
        print("uname: " + self.user.name)
        print("Bot ID: " + str(self.user.id))
        synced = await self.tree.sync()
        print("Slash commands synced?" + str(len(synced)))
#
#           MAINLOOP
#
if __name__ == "__main__":
    # READ TOKENS FROM .ENV FILE
    load_dotenv()   # Loads ./.env
    DISCORD_TOKEN = os.getenv('DISCORD_TOKEN')
    # Run client
    client = Client()
    client.run(DISCORD_TOKEN)
