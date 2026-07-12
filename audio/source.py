from abc import ABC, abstractmethod


class AudioSource(ABC):
    """Abstract class for Audio Sources"""

    @abstractmethod
    def read(self) -> bytes | None:
        """Read (PCM) audio bytes"""
    

    @property
    @abstractmethod
    def finished(self) -> bool:
        """True if the audio source is finished"""
