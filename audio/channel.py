from audio.queue import AudioQueue
from audio.source import AudioSource

class AudioChannel:
    """Class to abstract an audio channel for mixing"""
    def __init__(self):
        self.queue = AudioQueue()
        self.current: AudioSource | None = None
        self.effects = []   # Volume, mute, etc. are effects


    def read(self) -> bytes | None:
        # If current is None, get the next source from queue
        if self.current is None:
            self.current = self.queue.dequeue()
        # If current still None, queue is empty
        if self.current is None:
            return None
        # Read frame and if it's the last frame, get the next source
        frame = self.current.read()
        if self.current.finished:
            self.current = self.queue.dequeue()
        return frame


    def skip(self):
        """Skips the current song by setting current internally to None"""
        self.current = None


    def stop(self):
        """Stops playback and clears the queue"""
        self.queue.clear()
        self.current = None


    @property
    def finished(self) -> bool:
        """Returns True if the channel is empty"""
        return (
            self.current is None
            and self.queue.is_empty()
        )
