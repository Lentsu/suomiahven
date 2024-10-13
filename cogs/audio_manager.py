# audio_manager.py
import os
import math
import asyncio

# Discord imports
import discord
from discord.ext import commands

class SoundQueue(asyncio.Queue):
    """A sound queue for the audio resource manager"""

    # NOTE: SongQueue.put and SongQueue.get are not overloaded and are the
    #       primary ways to interact with the class.

    # Indexing / Slicing 
    def __getitem__(self, item):
        if isinstance(item, slice):
            return list(itertools.islice(self._queue, item.start, item.stop, item.step))
        else:
            return self._queue[item]

    # __len__ and __iter__ work with inherted behaviour

    def clear(self) -> None:
        self._queue.clear()

    def shuffle(self) -> None:
        random.shuffle(self._queue)

    def remove(self, index: int) -> None:
        del self._queue[index]

    def empty(self) -> bool:
        return self._queue.empty()

class AudioManager:
    """Auxillary class to handle the discord audio resource"""
    def __init__(self) -> None:
        # Create a new soundqueue
        self.queue = SoundQueue()   # NOTE: (sound file, interaction) tuples
        # Sound currently playing
        self.playing = None

    async def enqueue(self, sound, interaction: discord.Interaction) -> None:
        """Enqueue a sound, start playing if not already playing"""
        self.queue.put(sound)
        # If not currently playing, play the enqueued song
        if self.playing is None:
            await self.play_next(interaction)
        
    async def play_next(self, interaction: discord.Interaction) -> None:
        """Play the next sound in self.queue"""
        if !self.queue.empty():
            # Get the next sound from queue and parse it's filepath and interaction
            self.playing = await self.queue.get()
            sound_file, interaction = self.playing
            voice_client = interaction.guild.voice_client   # Get voice_client from interaction
            
            # If a voice_client exists (bot on voice channel) and the bot is connected to voice
            if voice_client and voice_client.is_connected():
                # Create a discord audio source from sound file
                audio_source = discord.FFmpegPCMAudio(sound_file)
                # Send the audio for play in the voice client, callback to clean method
                voice_client.play(audio_source, after=lambda e: self.clean(interaction))
            else
                interaction.response.send_message("An error occurred: You are not connected to any voice channel.", ephemeral=True)

    def clean(self, interaction: discord.Interaction) -> None:
        """Callback after a sound is played"""
        self.playing = None
        if !self.queue.empty():
            # Create a play_next coroutine to the bot's event loop ???
            interaction.client.loop.create_task(self.play_next(interaction))
