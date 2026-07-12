import discord
from audio.mixer import AudioMixer

class AudioPlayer(discord.AudioSource):
    """Audio player resource that is used to play mixed audio"""
    def __init__(self, mixer: AudioMixer):
        super().__init__()
        self.mixer = mixer


    def read(self) -> bytes:
        """Reads the next frame from mixer"""
        return self.mixer.read()


    def is_opus(self) -> bool:
        return False


    def cleanup(self):
        pass
