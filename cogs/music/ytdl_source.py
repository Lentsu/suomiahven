# ytdl_source.py

import asyncio
import subprocess
from typing import ClassVar

import yt_dlp

from audio.source import AudioSource
from audio.mixer import SAMPLE_RATE, CHANNELS, FRAME_BYTES


class YTDLSource(AudioSource):
    """AudioSource implementation with yt-dlp + FFMPEG"""

    YTDL_OPTIONS: ClassVar = {
        'format': 'bestaudio/best',
        'noplaylist': True,
        'nocheckcertificate': True,
        'ignoreerrors': False,
        'logtostderr': False,
        'quiet': True,
        'no_warnings': True,
        'default_search': 'auto',
        'source_address': '0.0.0.0',
    }

    ytdl = yt_dlp.YoutubeDL(YTDL_OPTIONS)


    @classmethod
    async def create(cls, search: str) -> "YTDLSource":
        """Factory to create a YTDLSource from search"""
        
        loop = asyncio.get_running_loop()

        result = await loop.run_in_executor(
            None,
            lambda: cls.ytdl.extract_info(
                search,
                download=False,
            ),
        )

        # Return the first result entry
        if "entries" in result:
            result = result["entries"][0]
        
        return cls(result)


    def __init__(self, metadata: dict):
        self.metadata = metadata 
        
        self.uploader       = metadata.get('uploader')
        self.uploader_url   = metadata.get('uploader_url')
        date                = metadata.get('upload_date')
        self.upload_date    = date[6:8] + '.' + date[4:6] + '.' + date[0:4]
        self.title          = metadata.get('title')
        self.thumbnail      = metadata.get('thumbnail')
        self.description    = metadata.get('description')
        self.duration       = self.parse_duration(int(metadata.get('duration')))
        self.tags           = metadata.get('tags')
        self.url            = metadata.get('webpage_url')
        self.views          = metadata.get('view_count')
        self.likes          = metadata.get('like_count')
        self.dislikes       = metadata.get('dislike_count')
        self.stream_url     = metadata.get('url')

        self._finished = False

        # Spawn an FFmpeg subprocess
        self._process = subprocess.Popen(
            [
                FFMPEG_EXECUTABLE,
                "-nostdin",
                "-reconnect", "1",
                "-reconnect_streamed", "1",
                "-reconnect_delay_max", "5",
                "-i", self.stream_url,
                "-f", "s16le",
                "-acodec", "pcm_s16le",
                "-ar", str(SAMPLE_RATE),
                "-ac", str(CHANNELS),
                "-"
            ],
            stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL,
        )

    
    def read(self) -> bytes | None:
        """Reads the next PCM frame from FFmpeg"""
        if self._finished:
            return None

        frame = self._process.stdout.read(FRAME_BYTES)

        if len(frame) != FRAME_BYTES:
            self._finished = True
            self.cleanup()
            return None

        return frame


    @property
    def finished(self) -> bool:
        """Returns True when playback has finished"""
        return self._finished


    def cleanup(self):
        """Ends the FFmpeg subprocess"""

        if self._process.poll() is None:
            self._process.kill()

        if self._process.stdout is not None:
            self._process.stdout.close()

        self._process.wait()
