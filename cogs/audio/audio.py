#   audio.py

from discord.ext import commands
from discord import app_commands
import discord

class Audio(commands.Cog):
    """Voice connection commands."""

    def __init__(self, client) -> None:
        self.client = client

    @app_commands.command(name="join")
    async def join(self, interaction: discord.Interaction) -> None:
        """Joins your current voice channel."""
        
        if interaction.guild is None:
            await interaction.response.send_message("You are not on any "
                                                    "server.", ephemeral=True)
            return

        if interaction.user.voice is None:
            await interaction.response.send_message("You are not on any "
                                                    "voice channel.",
                                                    ephemeral=True)
            return

        # Get session from client.audio (AudioManager)
        session = self.client.audio.get_session(interaction.guild.id)

        await session.connect(interaction.user.voice.channel)

        await interaction.response.send_message(
            f"Joined **{interaction.user.voice.channel.name}**."
        )


    @app_commands.command(name="leave")
    async def leave(self, interaction: discord.Interaction) -> None:
        """Leaves the current voice channel"""

        if interaction.guild is None:
            await interaction.response.send_message("You are not on any "
                                                    "server.", ephemeral=True)
            return

        # Get session from client.audio (AudioManager)
        session = self.client.audio.get_session(interaction.guild.id)

        await session.disconnect()

        self.client.audio.remove_session(interaction.guild.id)

        await interaction.response.send_message("Disconnected.")

