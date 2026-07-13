#   music.py

from discord.ext import commands
from discord import app_commands
import discord

from music.source import YTDLSource
from music.song import YTDLSource


class Music(commands.Cog):
    """Music playback commands"""

    MUSIC_CHANNEL = "music"


    def __init__(self, client) -> None:
        self.client = client


    def _channel(self, interaction: discord.Interaction):
        """Get or register the AudioSession and music AudioChannel"""
        session = self.client.audio.get_session(interaction.guild.id)
        return session.mixer.get_channel(self.MUSIC_CHANNEL)


    @app_commands.command(name="play")
    @ensure_connected
    async def play(self, interaction: discord.Interaction, search: str) -> None:
        """Enqueues a song to the music AudioChannel"""

        await interaction.response.defer()

        channel = self._channel(interaction)

        source = await YTDLSource.create(search)
        song = Song(source, interaction.user)
