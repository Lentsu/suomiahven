#   ahven.py
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

#
#           MAINLOOP
#
def main():

    # READ TOKENS FROM .ENV FILE
    load_dotenv()   # Loads ./.env
    DISCORD_TOKEN = os.getenv('DISCORD_TOKEN')

    # Init client
    client = commands.Bot(command_prefix='/', intents=discord.Intents.default())

    # List of 'Cogs' (class extensions for bot events and commands)
    cogs_files = [
        'greeter'
    ]

    # Load all 'Cogs' as client extensions
    for file in cogs_files:
        client.load_extension(f"cogs.{file}")

    # Run the bot
    client.run(DISCORD_TOKEN)

# Only run main if file was run directly by the interpreter
if __name__ == "__main__":
    main()
