"""
Suomiahven
==========

An extensible and modular Finnish Discord bot written for personal use.

main.py : Entry point for the client.
Initializes configuration, loads extensions, and starts the Discord client.
"""
import os
import logging
import yaml
import discord
from discord.ext import commands
from dotenv import load_dotenv

from audio.manager import AudioManager


__author__      = "Lentsu, Veritorakka"
__copyright__   = "Free to use"

# Use logger with settings
logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s] %(levelname)-8s %(name)s: %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger(__name__)


class SuomiAhven(commands.Bot):
    """Toplevel client for Suomiahven"""
    def __init__(self, config):
        self.config = config
        super().__init__(
            command_prefix=commands.when_mentioned_or(self.config["bot"]["prefix"]),
            intents=discord.Intents.all(),
        )
        self.cogs_list = self.config["cogs"]
        self.audio = AudioManager()


    # Load Cogs 
    async def setup_hook(self):
        for cog in self.cogs_list:
            logger.info(f"Loading {cog}")
            await self.load_extension(f"cogs.{cog}")


    # When connection is made
    async def on_ready(self):

        logger.info("uname: " + self.user.name)
        logger.info("Bot ID: " + str(self.user.id))

        # Global sync the slash commands (if enabled)
        if self.config["bot"]["sync_commands"]:
            synced = await self.tree.sync()
            logger.info("Slash commands synced: " + str(len(synced)))

        # Log the synced slash commands
        for command in self.tree.walk_commands():
            logger.info(f"/{command.name}")

        # Log the activity status
        status = self.config["bot"]["activity"]
        await self.change_presence(activity=discord.Game(name=status))


def main():
    # READ secrets from .env file
    load_dotenv()
    DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
    # READ config.yml
    with open("config.yml") as f:
        config = yaml.safe_load(f)
    client = SuomiAhven(config)
    client.run(DISCORD_TOKEN)


# If this script was called directly
if __name__ == "__main__":
    main()
