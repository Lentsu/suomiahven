from abc import ABC, abstractmethod

import discord

from audio.source import AudioSource


class PlaybackItem(ABC):
    """Abstract class for items in channel playback queue"""
    @property
    @abstractmethod
    def source(self) -> AudioSource:
        ...


    @abstractmethod
    def create_embed(self) -> discord.embed:
        ...
