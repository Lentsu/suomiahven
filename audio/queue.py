from collections import deque
from typing import Optional
from audio.source import AudioSource


class AudioQueue:
    """Audio Queue for different sources."""
    def __init__(self):
        self._queue = deque()
    

    def enqueue(self, source: AudioSource) -> None:
        """Enqueue an AudioSource"""
        self._queue.append(source)          # Appends to right


    def dequeue(self) -> Optional[AudioSource]:
        """Dequeue the next AudioSource from the queue (if any)"""
        if self._queue:
            return self._queue.popleft()    # Pops from left
        return None


    def peek(self, i=0) -> Optional[AudioSource]:
        """Look at the i:th (default 0) AudioSource without dequeueing it (if any)"""
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
