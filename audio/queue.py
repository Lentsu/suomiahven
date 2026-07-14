from collections import deque
from typing import Optional
from audio.playback_item import PlaybackItem 


class AudioQueue:
    """Audio Queue for different PlaybackItems."""
    def __init__(self):
        self._queue = deque()
        self.loop = False

    def enqueue(self, item: PlaybackItem) -> None:
        """Enqueue a PlaybackItem"""
        self._queue.append(item)            # Appends to right


    def dequeue(self) -> Optional[PlaybackItem]:
        """Dequeue the next PlaybackItem from the queue (if any)"""
        if self._queue:
            return self._queue.popleft()    # Pops from left
        return None


    def remove(self, index: int) -> Optional[PlaybackItem]:
        """Dequeue the PlaybackItem pointed by index from the queue (if any)"""
        items = list(self._queue)
        item = items.pop(index)
        self._queue = deque(items)
        return item


    def shuffle(self):
        """Shuffle the queue"""
        items = list(self._queue)
        random.shuffle(items)
        self._queue = deque(items)


    def move(self, index: int, new: int):
        """Moves PlaybackItem at index to new in the queue"""
        items = list(self._queue)
        item = items.pop(index)
        items.insert(new, item)
        self._queue = deque(items)
        

    def peek(self, i=0) -> Optional[PlaybackItem]:
        """Look at the i:th (default 0) PlaybackItem without dequeueing it (if any)"""
        if 0 <= i < len(self._queue):
            return self._queue[i]
        return None


    def clear(self) -> None:
        """Clears the audio queue"""
        self._queue.clear()


    def is_empty(self) -> bool:
        """Returns true if the queue is empty"""
        return len(self._queue) == 0


    def __len__(self):
        return len(self._queue)
