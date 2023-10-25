#   music.py

# For os stuff
import os

# Discord related stuff
from discord.ext import commands
from discord import app_commands
import discord

# YTDLP library to stream the music from youtube 
import yt_dlp

# GET FFMPEG_EXECUTABLE LOCATION FROM LOCAL ENVIRONMENT
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
from dotenv import load_dotenv
load_dotenv()
FFMPEG_EXECUTABLE = os.getenv("FFMPEG_PATH")
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
# Auxillary Class to search yt 
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
# Options for YTDL
class YT:
    def __init__(self) -> None:
        self.YTDL_OPTIONS = {
            'format': 'bestaudio/best', # Best audio format
            'noplaylist': True,         # Don't accept playlists
            'quiet': True,              # Be quiet
        }

        self.ytdl = yt_dlp.YoutubeDL(self.YTDL_OPTIONS) # NOTE: is this just ytdl?

    # Search Youtube and return url if something is found
    def search_yt(self, item):
        try:
            # Try to search and extract info from the first result in youtube
            info = self.ytdl.extract_info("ytsearch:%s" % item, download=False)['entries'][0]
        except Exception:
            print("Couldn't find SONG!!!")
            return False
        # Return the info as a custom pair (url, title) if found.
        return {'source': info['formats'][0]['url'], 'title': info['title']}


# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
# Class to create a modulated PCMAudio source 
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
class Modulator:
    # Constructor
    def __init__(self) -> None:
        self.bass = 1
        self.speed = 1

    # Options for FFmpeg postprocessor
    FFMPEG_OPTIONS = {
        'options': '-vn',       # Verbose, no-overwrite
        'executable':FFMPEG_EXECUTABLE,
        'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5'
    }

    # Create a FFmpegPCMAudio music source from URL
    def create_source(self, url):
        # Create the source and return it
        return discord.FFmpegPCMAudio(url, **self.FFMPEG_OPTIONS)
    

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
# The music Cog containing all the app commands
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
class Music(commands.Cog):
    # Constructor
    def __init__(self, client) -> None:
        self.client = client

        # YT Auxillary class instance
        self.YT = YT()

        # Modulator instance!
        self.modulator = Modulator()

        # IMPORTANT MEMBERS:
        self.is_playing = False     # Indicates wheter the bot is currently playing
        self.voice_channel = None   # Type is discord.voice_channel
        self.play_queue = []        # Contains pairs (url, title)

    # Play next song in queue until queue is empty
    def play_next(self) -> None:

        # If there is music in the queue
        if len(self.play_queue) > 0:
            self.is_playing = True # Change state to playing

            # Get the url of the first song in the queue
            url = self.play_queue[0][0]['source']
            print(url)

            # Create a source from the url
            source = self.modulator.create_source(url)
            
            self.play_queue.pop(0) # Remove the song from queue

            # Play the source audio and call this method again recursively
            self.vc.play(source, after=lambda e: self.play_next())
        else:
            # When queue is empty
            self.is_playing = False # Change state to not playing


    async def play_music(self, interaction: discord.Interaction):
        # If there is music in the queue
        if len(self.play_queue) > 0:
            self.is_playing = True # Change state to playing
            
            # Get the url of the first song in the queue and make a source out of it
            url = self.play_queue[0][0]['source']
            print(url)
            source = self.modulator.create_source(url)

            # If no voice channel or not connected to that
            if self.voice_channel == None or not self.voice_channel.is_connected():
                self.voice_channel = await self.play_queue[0][1].connect()

                # If can't connect to VoiC
                if self.voice_channel == None:
                    await interaction.response.send_message(":fish: Can't connect to voice :fish:");
                    return
            else:
                # Move to the voice channel specified in play queue 
                await self.voice_channel.move_to(self.play_queue[0][1])

            # Remove the first song in queue and play it
            self.play_queue.pop(0)
            self.voice_channel.play(source, after=lambda e: self.play_next)

        # Else, queue is empty
        else:
            self.is_playing = False


    # PLAY COMMAND!
    @app_commands.command(name="play")
    async def play(self, interaction: discord.Interaction, search: str) -> None:
        """ Search and play music """

        # Get the voice state of the caller
        voice = interaction.user.voice
        if voice == None:
            await interaction.response.send_message(":fish: Join a voice channel first! :fish:")
        else:
            voice_channel = voice.channel
            song = self.YT.search_yt(search)
            if type(song) == type(True): # If search failed!
                await interaction.response.send_message(":man_shrugging: Can't find that... :man_shrugging:", ephemeral=True)
            else:
                await interaction.response.send_message(f":fishing_pole_and_fish: Enqueued {song['title']}")
                self.play_queue.append([song, voice_channel])
    
                # If not playing already, call play_music
                if self.is_playing == False:
                    await self.play_music(interaction)

    # SKIP COMMAND
    @app_commands.command(name="skip")
    async def skip(self, interaction: discord.Interaction) -> None:
        if self.voice_channel != None and self.voice_channel:
            # Stop playing music (current song)
            self.voice_channel.stop()
            # Call the play music again
            await self.play_music(interaction)

    # JOIN COMMAND


    # LEAVE COMMAND!
    @app_commands.command(name="leave")
    async def leave(self, interaction: discord.Interaction) -> None:
        # If on a voice channel
        if self.voice_channel == None:
            await interaction.response.send_message(":bubbles:")
        else:
            self.is_playing = False
            await self.voice_channel.disconnect()


async def setup(client: commands.Bot) -> None:
    try:
        await client.add_cog(Music(client))
        print ("[OK]")
    except:
        print ("[ERROR]")

