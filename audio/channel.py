from audio.queue import AudioQueue
from audio.source import AudioSource

class AudioChannel:
    """Class to abstract an audio channel for mixing"""
    def __init__(self):
        self.queue = AudioQueue()
        self.current: AudioSource | None = None
        self.effects = []   # Volume, mute, etc. are effects

    @property
    def finished(self) -> bool:
        """Returns True if the channel is empty"""
        return (
            self.current is None
            and self.queue.is_empty()
        )
