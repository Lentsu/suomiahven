from audio.queue import AudioQueue
from audio.source import PlaybackItem


class AudioChannel:
    """Class to abstract an audio channel for mixing"""
    def __init__(self):
        self.queue = AudioQueue()
        self.current: PlaybackItem | None = None
        self.volume = 1.0
        self._paused: bool = False


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


    def enqueue(self, item: PlaybackItem):
        """Adds the PlaybackItem to AudioQueue"""
        self.queue.enqueue(item)


    def shuffle(self):
        """Shuffles the AudioQueue"""
        self.queue.shuffle()


    def remove(self, index: int):
        """Removes the index item from AudioQueue"""
        self.queue.remove(index)


    def move(self, index: int, new: int):
        """Moves the PlaybackItem at index to new in AudioQueue"""
        self.queue.move(index, new)


    def skip(self):
        """Skips the current song by setting current internally to None"""
        self.current = None


    def stop(self):
        """Stops playback and clears the queue"""
        self.queue.clear()
        self.current = None

    
    def pause(self):
        """Pauses the channel"""
        self._paused = True


    def resume(self):
        """Unpauses the channel"""
        self._paused = False


    @property
    def paused(self) -> bool:
        """Returns true if the channel is paused"""
        return self._paused


    @property
    def empty(self) -> bool:
        """Returns True if the queue is empty"""
        return len(self.queue) == 0


    @property
    def finished(self) -> bool:
        """Returns True if the channel is empty"""
        return (
            self.current is None
            and self.queue.is_empty()
        )
    

    def __len__(self):
        return len(self.queue)
