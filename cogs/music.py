import os

import asyncio
import functools
import itertools
import math
import random
from typing import Optional
from async_timeout import timeout
import pyttsx3
import tempfile
from pydub import AudioSegment

import yt_dlp

from discord.ext import commands
from discord import app_commands
import discord

# Import auxillary functions 
from cogs.auxillary import try_wrap

# Read required secrets from the ROOT ENV file
from dotenv import load_dotenv
load_dotenv()
FFMPEG_EXECUTABLE = os.getenv("FFMPEG_PATH")

def adjust_volume(file_path, volume_change_dB):
    sound = AudioSegment.from_file(file_path)
    louder_sound = sound + volume_change_dB
    louder_sound.export(file_path, format="wav")

async def async_text_to_speech(text, volume_change_dB=40, speech_rate=125):
    def synch_text_to_speech():
        engine = pyttsx3.init()
        temp_file, temp_file_path = tempfile.mkstemp(suffix='.wav')
        os.close(temp_file)  # Suljetaan tiedosto välittömästi sen luomisen jälkeen

        engine.setProperty('rate', speech_rate)
        engine.save_to_file(text, temp_file_path)
        engine.runAndWait()

        # Nosta äänitiedoston äänenvoimakkuutta
        adjust_volume(temp_file_path, volume_change_dB)
        
        return temp_file_path
    
    # Suorittaa synkronisen funktion asynkronisesti
    return await asyncio.to_thread(synch_text_to_speech)

# Silence useless bug reports messages
yt_dlp.utils.bug_reports_message = lambda: ''

class VoiceError(Exception):
    pass

class YTDLError(Exception):
    pass

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

    def __init__(self, interaction: discord.Interaction, source: discord.FFmpegPCMAudio, *, data: dict, volume: float = 0.5):
        super().__init__(source, volume)

        self.requester = interaction.user
        self.channel = requester.voice.channel 
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

    def __str__(self):
        return '**{0.title}** by **{0.uploader}**'.format(self)

    @classmethod
    async def create_source(cls, interaction: discord.Interaction, search: str, *, loop: asyncio.BaseEventLoop = None):
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
    def parse_duration(duration: int):
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

class Song:
    __slots__ = ('source', 'requester')

    def __init__(self, source: YTDLSource):
        self.source = source
        self.requester = source.requester

    def create_embed(self):
        embed = (discord.Embed(title='Now playing',
                               description='```css\n{0.source.title}\n```'.format(self),
                               color = 16202876)
                 .add_field(name='Duration', value=self.source.duration)
                 .add_field(name='Requested by', value=self.requester.mention)
                 .add_field(name='Uploader', value='[{0.source.uploader}]({0.source.uploader_url})'.format(self))
                 .add_field(name='URL', value='[Click]({0.source.url})'.format(self))
                 .set_thumbnail(url=self.source.thumbnail))

        return embed

class SongQueue(asyncio.Queue):
    def __getitem__(self, item):
        if isinstance(item, slice):
            return list(itertools.islice(self._queue, item.start, item.stop, item.step))
        else:
            return self._queue[item]

    def __iter__(self):
        return self._queue.__iter__()

    def __len__(self):
        return self.qsize()

    def clear(self):
        self._queue.clear()

    def shuffle(self):
        random.shuffle(self._queue)

    def remove(self, index: int):
        del self._queue[index]

class VoiceState:
    def __init__(self, interaction: discord.Interaction):
        self.bot = interaction.client
        self._interaction = interaction

        self.current = None
        self.voice = None
        self.next = asyncio.Event()
        self.songs = SongQueue()

        self._loop = False
        self._volume = 1
        self.skip_votes = set()

        self.audio_player = bot.loop.create_task(self.audio_player_task())

    def __del__(self):
        self.audio_player.cancel()

    @property
    def loop(self):
        return self._loop

    @loop.setter
    def loop(self, value: bool):
        self._loop = value

    @property
    def volume(self):
        return self._volume

    @volume.setter
    def volume(self, value: float):
        self._volume = value

    @property
    def is_playing(self):
        return self.voice and self.current

    async def audio_player_task(self):
        while True:
            self.next.clear()
            try:
                async with timeout(300):  # 5 minutes
                    self.current = await self.songs.get()
            except asyncio.TimeoutError:
                await self.stop()
                return

            self.current.source.volume = self._volume
            self.voice.play(self.current.source, after=lambda e: self.bot.loop.call_soon_threadsafe(self.next.set))
            await interaction.response.send_message(embed=self.current.create_embed(), ephemeral=True)
            await self.next.wait()

            if self.loop:
                # Kutsu play-komentoa uudelleen samalla URL-linkillä
                interaction = self.interaction
                interaction.user.voice = self
                await interaction.invoke(self.bot.get_command('play'), search=self.current.source.url)

            await asyncio.sleep(1)  # Odota sekunti ennen seuraavan kappaleen soittamista

    async def play_next_song(self, error: Optional[Exception]):
        if error:
            await interaction.response.send_message('An error occurred: {}'.format(str(error)), ephemeral=True)
        if self.loop:
            await self.songs.put(self.current)
        self.next.set()

    def skip(self):
        self.skip_votes.clear()

        if self.is_playing:
            self.voice.stop()

    async def stop(self):
        if self.voice:
            await self.voice.disconnect()
            self.voice = None
        else:
            raise VoiceError('Bot is not connected to any voice channel.')

        self.songs.clear()

class Music(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.voice_states = {}

    def get_voice_state(self, interaction: discord.Interaction):
        state = self.voice_states.get(interaction.guild_id)
        if not state:
            state = VoiceState(self.bot, interaction)
            self.voice_states[interaction.guild_id] = state

        return state

    def cog_unload(self):
        for state in self.voice_states.values():
            self.bot.loop.create_task(state.stop())

    def cog_check(self, intearction: discord.Interaction):
        if not interaction.guild:
            raise commands.NoPrivateMessage('This command can\'t be used in DM channels.')

        return True

    async def cog_before_invoke(self, interaction: discord.Interaction):
        interaction.user.voice = self.get_voice_state(interaction)

    async def cog_command_error(self, interaction: discord.Interaction, error: commands.CommandError):
        await interaction.response.send_message('An error occurred: {}'.format(str(error)), ephemeral=True)

    @app_commands.command(name='join')
    async def _join(self, interaction: discord.Interaction):
        """Joins a voice channel."""
    
        # Check if the user is in a voice channel
        if get_voice_state(interaction):
            destination = interaction.user.voice.channel
        if interaction.user.voice:       # NOTE: interaction.voice_state may not be a thing!
            await interaction.user.voice.move_to(destination)
            return

        interaction.user.voice = await destination.connect()  #NOTE HERE TOO
        await interaction.response.send_message('✅')

    @app_commands.command(name='summon')
    @commands.has_permissions(manage_guild=True)
    async def _summon(self, interaction: discord.Interaction, *, channel: discord.VoiceChannel = None):
        """Summons the bot to a voice channel.

        If no channel was specified, it joins your channel.
        """

        if not channel and not interaction.user.voice:
            raise VoiceError('You are neither connected to a voice channel nor specified a channel to join.')

        destination = channel or interaction.author.voice.channel
        if interaction.user.voice:
            await interaction.user.voice.move_to(destination)  # NOTE INTERACTION.VOICE_STATE USED HERE
            return

        interaction.user.voice = await destination.connect()

    @app_commands.command(name='leave')
    @commands.has_permissions(manage_guild=True)
    async def _leave(self, interaction: discord.Interaction):
        """Clears the queue and leaves the voice channel."""

        # NOTE INTERACTION.VOICE_STATE USED HEERE
        if not interaction.user.voice:
            return await interaction.response.send_message('Not connected to any voice channel.')
        if interaction.user.voice.loop == True:
            interaction.user.voice.loop = not interaction.voice_state.loop
        await interaction.user.voice.stop()
        del self.voice_states[interaction.guild_id]
        await interaction.response.send_message('✅')


    @app_commands.command(name='now')
    async def _now(self, interaction: discord.Interaction):
        """Displays the currently playing song."""
        if not interaction.user.voice.current:
            return await interaction.response.send_message('Nothing is currently playing.')

        await interaction.response.send_message(embed=interaction.user.voice.current.create_embed())

    @app_commands.command(name='pause')
    @commands.has_permissions(manage_guild=True)
    async def _pause(self, interaction: discord.Interaction):
        """Pauses the currently playing song."""

        if interaction.user.voice.is_playing and interaction.voice_state.voice.is_playing():
            interaction.user.voice.pause()
            await interaction.response.send_message('⏸️')

    @app_commands.command(name='resume')
    @commands.has_permissions(manage_guild=True)
    async def _resume(self, interaction: discord.Interaction):
        """Resumes a currently paused song."""

        if interaction.user.voice.is_playing and interaction.voice_state.voice.is_paused():
            interaction.user.voice.resume()
            await interaction.response.send_message('▶️')

    @app_commands.command(name='stop')
    @commands.has_permissions(manage_guild=True)
    async def _stop(self, interaction: discord.Interaction):
        """Stops playing song and clears the queue."""

        interaction.user.voice.songs.clear()

        if interaction.user.voice.is_playing:
            interaction.user.voice.stop()
            await interaction.response.send_message('⏹')

    @app_commands.command(name='skip')
    async def _skip(self, interaction: discord.Interaction):
        """Skip the currently playing song."""

        if not interaction.user.voice.is_playing:
            return await interaction.response.send_message('Not playing any music right now...')

        interaction.user.voice.skip()
        await interaction.response.send_message('⏭')

    @app_commands.command(name='queue')
    async def _queue(self, interaction: discord.Interaction, *, page: int = 1):
        """Shows the player's queue.

        You can optionally specify the page to show. Each page contains 10 elements.
        """

        if len(interaction.user.voice.songs) == 0:
            return await interaction.response.send_message('Empty queue.')

        items_per_page = 10
        pages = math.ceil(len(interaction.user.voice.songs) / items_per_page)

        start = (page - 1) * items_per_page
        end = start + items_per_page

        queue = ''
        for i, song in enumerate(interaction.user.voice.songs[start:end], start=start):
            queue += '`{0}.` [**{1.source.title}**]({1.source.url})\n'.format(i + 1, song)

        embed = (discord.Embed(description='**{} tracks:**\n\n{}'.format(len(interaction.user.voice.songs), queue))
                 .set_footer(text='Viewing page {}/{}'.format(page, pages)))
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name='shuffle')
    async def _shuffle(self, interaction: discord.Interaction):
        """Shuffles the queue."""

        if len(interaction.user.voice.songs) == 0:
            return await interaction.response.send_message('Empty queue.')

        interaction.user.voice.songs.shuffle()
        await interaction.response.send_message('✅')

    @app_commands.command(name='remove')
    async def _remove(self, interaction: discord.Interaction, index: int):
        """Removes a song from the queue at a given index."""

        if len(interaction.user.voice.songs) == 0:
            return await interaction.response.send_message('Empty queue.')

        interaction.user.voice.songs.remove(index - 1)
        await interaction.response.send_message('✅')

    @app_commands.command(name='loop')
    async def _loop(self, interaction: discord.Interaction):
        """Loops the currently playing song."""
        if not interaction.user.voice.is_playing:
            return await interaction.response.send_message('Nothing is currently playing.')

        interaction.user.voice.loop = not interaction.voice_state.loop
        print("Loop is now", "enabled" if interaction.user.voice.loop else "disabled")
        await interaction.response.send_message('Loop is now ' + ('enabled' if interaction.user.voice.loop else 'disabled'))


    
    @app_commands.command(name='puhu')
    async def _puhu(self, interaction, *, teksti: str):
        """Muuttaa annetun tekstin puheeksi ja toistaa sen äänikanavalla."""
        if not interaction.user.voice:
            await interaction.response.send_message("Sinun täytyy olla äänikanavalla käyttääksesi tätä komentoa.")
            return

        # Get the context (for invoke)
        ctx = await self.client.get_context(interaction)

        # Join the voice channel if not already there
        if not interaction.user.voice:
            await ctx.invoke(self._join)

        tts_filename = await async_text_to_speech(teksti)  # Muutettu käyttämään asynkronista versiota
        await interaction.voice_client.play(discord.FFmpegPCMAudio(executable=FFMPEG_EXECUTABLE, source=tts_filename), after=lambda e: print('TTS valmis.', e))

        # Tiedoston siivous
        os.remove(tts_filename)


    @app_commands.command(name='play')
    async def _play(self, interaction: discord.Interaction, *, search: str):
        """Plays a song.

        If there are songs in the queue, this will be queued until the
        other songs finished playing.

        This command automatically searches from various sites if no URL is provided.
        A list of these sites can be found here: https://rg3.github.io/youtube-dl/supportedsites.html
        """

        # Get the context (for invoke)
        ctx = await self.client.get_context(interaction)


        print("Play command invoked.")
        if not interaction.user.voice:
            await ctx.invoke(self._join)

            try:
                source = await YTDLSource.create_source(interaction, search, loop=self.bot.loop)
            except YTDLError as e:
                await interaction.response.send_message('An error occurred while processing this request: {}'.format(str(e)))
        else:
            song = Song(source)
            await interaction.user.voice.songs.put(song)
            await interaction.response.send_message('Enqueued {}'.format(str(source)))

    async def ensure_voice_state(self, interaction: discord.Interaction):
        if not interaction.user.voice or not interaction.user.voice.channel:
            raise commands.CommandError('You are not connected to any voice channel.')

        if interaction.voice_client:
            if interaction.voice_client.channel != interaction.user.voice.channel:
                raise commands.CommandError('Bot is already in a voice channel.')

@try_wrap
async def setup(client: commands.Bot) ->None:
    await client.add_cog(Music(client))

