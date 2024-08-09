#   music.py
import os
import math
import asyncio

# Discord imports
from discord.ext import commands
from discord import app_commands
import discord

# Import local auxillary functions
from cogs.auxillary import try_wrap

# 3rd party imports
import yt_dlp

# Read required secrets from the ROOT ENV file
from dotenv import load_dotenv
load_dotenv()
FFMPEG_EXECUTABLE = os.getenv("FFMPEG_PATH")

# - - - - - - AUXILLARY CLASSES - - - - - -

# A class for creating Youtube Sources
class YTDLSource(discord.PCMVolumeTransformer):
    YTDL_OPTIONS = {
        'format': 'bestaudio/best',
        'extractaudio': True,
        'audioformat': 'mp3',
        'outtmpl': '%(extractor)s-%(id)s-%(title)s.%(ext)s',
        'restrictfilenames': True,
        'noplaylist': True,
        'nocheckcertificate': True,
        'ignoreerrors': False,
        'logtostderr': False,
        'quiet': True,
        'no_warnings': True,
        'default_search': 'auto',
        'source_address': '0.0.0.0',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
        'postprocessor_args': [
            '-ar', '48000',
            '-vn',
            '-b:a', '192k',
            '-f', 'mp3'
        ],
    }

    FFMPEG_OPTIONS = {
        'options': '-vn',
        'executable':FFMPEG_EXECUTABLE,
        'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5',
    }

    ytdl = yt_dlp.YoutubeDL(YTDL_OPTIONS)


    def __init__(self, interaction: discord.Interaction, source: discord.FFmpegPCMAudio, *, data: dict, volume: float = 0.5) -> None:
        super().__init__(source, volume)

        self.requester = interaction.user
        self.channel = interaction.channel
        self.data = data

        self.uploader = data.get('uploader')
        self.uploader_url = data.get('uploader_url')
        date = data.get('upload_date')
        self.upload_date = date[6:8] + '.' + date[4:6] + '.' + date[0:4]
        self.title = data.get('title')
        self.thumbnail = data.get('thumbnail')
        self.description = data.get('description')
        self.duration = self.parse_duration(int(data.get('duration')))
        self.tags = data.get('tags')
        self.url = data.get('webpage_url')
        self.views = data.get('view_count')
        self.likes = data.get('like_count')
        self.dislikes = data.get('dislike_count')
        self.stream_url = data.get('url')

    def __str__(self) -> str:
        return '**{0.title}** by **{0.uploader}**'.format(self)

    @classmethod
    # NOTE: cls is like self but for class instances
    async def create_source(cls, interaction: discord.Interaction, search: str, *, loop: asyncio.BaseEventLoop = None): # TODO This returns YTDLSource, what's the return type??
        loop = loop or asyncio.get_event_loop()

        partial = functools.partial(cls.ytdl.extract_info, search, download=False, process=False)
        data = await loop.run_in_executor(None, partial)

        if data is None:
            raise YTDLError('Couldn\'t find anything that matches `{}`'.format(search))

        if 'entries' not in data:
            process_info = data
        else:
            process_info = None
            for entry in data['entries']:
                if entry:
                    process_info = entry
                    break

            if process_info is None:
                raise YTDLError('Couldn\'t find anything that matches `{}`'.format(search))

        webpage_url = process_info['webpage_url']
        partial = functools.partial(cls.ytdl.extract_info, webpage_url, download=False)
        processed_info = await loop.run_in_executor(None, partial)

        if processed_info is None:
            raise YTDLError('Couldn\'t fetch `{}`'.format(webpage_url))

        if 'entries' not in processed_info:
            info = processed_info
        else:
            info = None
            while info is None:
                try:
                    info = processed_info['entries'].pop(0)
                except IndexError:
                    raise YTDLError('Couldn\'t retrieve any matches for `{}`'.format(webpage_url))

        return cls(interaction, discord.FFmpegPCMAudio(info['url'], **cls.FFMPEG_OPTIONS), data=info)

    @staticmethod
    def parse_duration(duration: int) -> str:
        minutes, seconds = divmod(duration, 60)
        hours, minutes = divmod(minutes, 60)
        days, hours = divmod(hours, 24)

        duration = []
        if days > 0:
            duration.append('{} days'.format(days))
        if hours > 0:
            duration.append('{} hours'.format(hours))
        if minutes > 0:
            duration.append('{} minutes'.format(minutes))
        if seconds > 0:
            duration.append('{} seconds'.format(seconds))

        return ', '.join(duration)

# A class for making pretty Song embeds
class Song:
    __slots__ = ('source', 'requester')

    def __init__(self, source: YTDLSource) -> None:
        self.source = source
        self.requester = source.requester

    def create_embed(self) -> discord.Embed:
        embed = (
            discord.Embed(title='Now playing',
            description='```css\n{0.source.title}\n```'.format(self),
            color = 16202876
        )
           .add_field(name='Duration', value=self.source.duration)
           .add_field(name='Requested by', value=self.requester.mention)
           .add_field(name='Uploader', value='[{0.source.uploader}]({0.source.uploader_url})'.format(self))
           .add_field(name='URL', value='[Click]({0.source.url})'.format(self))
           .set_thumbnail(url=self.source.thumbnail))

        return embed

# A class for maintaining music queues
class SongQueue(asyncio.Queue):   # NOTE: Extends asyncio.Queue:
                                  # https://docs.python.org/3/library/asyncio-queue.html

    # Used for random accessing sections from the queue (used by the queue command)
    def __getitem__(self, item):
        if isinstance(item, slice):
            return list(itertools.islice(self._queue, item.start, item.stop, item.step))
        else:
            return self._queue[item]

    # NOTE: SongQueue.put and SongQueue.get are the primary ways to interact with the class

    def __iter__(self) -> None:
        return self._queue.__iter__()

    def __len__(self) -> None:
        return self.qsize()

    def clear(self) -> None:
        self._queue.clear()

    def shuffle(self) -> None:
        random.shuffle(self._queue)

    def remove(self, index: int) -> None:
        del self._queue[index]

# - - - - - - COG IMPLEMENTATION - - - - - -

# Commands and events for greeting users
class Music(commands.Cog):

    def __init__(self, client) -> None:
        self.client = client
        self.queues = {}

    @app_commands.command(name="join")
    async def _join(self, interaction: discord.Interaction) -> None:
        """ Joins the caller's voice channel """
        await interaction.response.send_message("", ephemeral=False)
    
    @app_commands.command(name="leave")
    async def _leave(self, interaction: discord.Interaction) -> None:
        """ Leaves the client's current voice channel """
        await interaction.response.send_message("Interaction response", ephemeral=False)

@try_wrap
async def setup(client: commands.Bot) -> None:
    """ Tries to load the Cog to the client and prints [OK] on success """
    await client.add_cog(Music(client))

