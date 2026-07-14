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
        channel.enqueue(song)

        await interaction.followup.send(f"Enqueued **{song.source.title}**.")


    @app_commands.command(name="skip")
    async def skip(self, interaction: discord.Interaction) -> None:
        """Skip the currently playing song."""
        channel = self._channel(interaction)

        if channel.current is None:
            await interaction.response.send_message(
                "Nothing is playing", ephemeral=True
            )
            return

        title = channel.current.title
        channel.skip()

        await interaction.response.send_message("Nothing is playing.")


    @app_commands.command(name="stop")
    async def stop(self, interaction: discord.Interaction) -> None:
        """Stops playing song and clears the queue."""
        channel = self._channel(interaction)
        
        if channel.current is None:
            await interaction.response.send_message(
                "Nothing is playing", ephemeral=True
            )
            return
        
        channel.stop()

        await interaction.response.send_message("Music playback stopped.")

    
    @app_commands.command(name="pause")
    async def pause(self, interaction: discord.Interaction) -> None:
        """Pauses the currently playing song"""
        channel = self._channel(interaction)

        if channel.current is None:
            await interaction.response.send_message(
                "Nothing is playing", ephemeral=True
            )
            return

        channel.pause()

        await interaction.response.send_message("Music playback **paused**.")


    @app_commands.command(name="resume")
    async def pause(self, interaction: discord.Interaction) -> None:
        """Resumes the currently paused song"""
        channel = self._channel(interaction)

        if channel.current is None or not channel.paused:
            await interaction.response.send_message(
                "Nothing is **paused**", ephemeral=True
            )
            return

        channel.resume()

        await interaction.response.send_message("Music playback **resumed**.")



    @app_commands.command(name="shuffle")
    async def shuffle(self, interaction: discord.Interaction) -> None:
        """Shuffles the queue."""
        channel = self._channel(interaction)

        if len(channel) < 2:
            await interaction.response.send_message(
                "Queue has too few items", ephemeral=True
            )
            return

        channel.shuffle()

        await interaction.response.send_message("Music playback **paused**.")


    @app_commands.command(name="remove")
    async def remove(self, interaction: discord.Interaction, index: app_commands.Range[int 1]) -> None:
        """Removes a song from the queue at a given index."""
        channel = self._channel(interaction)

        try
            removed = channel.remove(index - 1)
        except IndexError:
            await interaction.response.send_message(
                "Invalid queue index", ephemeral=True
            )
            return

        await interaction.response.send_message("Removed **{removed.title}** from the queue.")


    @app_commands.command(name="queue")
    async def queue(self, interaction: discord.Interaction) -> None:
        """Shows the queued items."""
        channel = self._channel(interaction)

        if channel.finished:
            await interaction.response.send_message("Queue is empty")
            return

        embed = discord.Embed(
            title="Music Queue",
            colour=discord.Colour.blurple(),
        )


        if channel.current is not None:
            embed.add_field(
                name="Now Playing",
                value=channel.current.source.title,
                inline=False,
            )

        if len(channel.queue):
            embed.add_field(
                name="Queue",
                value="\n".join(
                    f"[{i+1}]. {song.source.title}"
                    for i, song in enumerate(channel.queue)
                ),
                inline=False,
            )

        await interaction.response.send_message(embed=embed)


    @app_commands.command(name="now")
    async def now(self, interaction: discord.Interaction):
        """Displays the currently playing song."""
        channel = self._channel(interaction)

        if channel.current is None:
            await interaction.response.send_message(
                "Nothing is currently playing.",
                ephemeral=True,
            )
            return

        song = Song(channel.current, channel.current.requester)

        await interaction.response.send_message(
            embed=song.create_embed()
        )


    @app_commands.command(name="loop")
    async def loop(self, interaction: discord.Interaction):
        """Loops the currently playing song."""

        channel = self._channel(interaction)

        channel.loop = not channel.loop

        await interaction.response.send_message(
            f"Loop {'enabled' if channel.loop else 'disabled'}."
        )
