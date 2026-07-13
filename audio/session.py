import discord

from audio.player import AudioPlayer
from audio.mixer import AudioMixer

class AudioSession:
    """Represents per-guild audio session resource"""

    def __init__(self):
        self.voice_client: discord.VoiceClient | None = None
        self.mixer = AudioMixer()
        self.player = AudioPlayer(self.mixer)


    async def connect(self, channel: discord.VoiceChannel):
        """Connects to voice channel and starts the player"""
        if self.voice_client is None:
            self.voice_client = await channel.connect()
            self.voice_client.play(self.player)


    async def disconnect(self):
        """Disconnects from the current voice channel (if any)"""
        if self.voice_client is None:
            return
        await self.voice_client.disconnect()
        self.voice_client = None


    async def move(self, channel: discord.VoiceChannel):
        """Moves the bot to the current voice channel (if any)"""
        if self.voice_client is None:
            await self.connect(channel)
        else:
            await self.voice_client.move_to(channel)


    async def ensure_connected(self, channel: discord.VoiceChannel):
        """Connect to the right channel (if any)"""
        if self.voice_client is None:
            await self.connect(channel)
        elif self.voice_client.channel != channel:
            await self.move(channel)
    

    @property
    def idle(self):
        """Returns True if the client is idle on channel"""
        return (self.mixer.finished and self.voice_client is not None)

