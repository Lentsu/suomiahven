#   greeter.py

from discord.ext import commands
from discord import app_commands
import discord

# Music bot tools
import yt_dlp

# Music bot
class Music(commands.Cog):

    def __init__(self, client) -> None:
        self.client = client

        self.is_playing = {}
        self.is_paused = {}
        self.music_queue = {}
        self.queue_index = {}

        self.voice_channel = {}
            
        # Options for YTDL or rather YTDLP
        self.YTDLP_OPTIONS = {
            'format': 'bestaudio',
            'nonplaylist': 'True'
        }

        # Options for FFMPEG
        self.FFMPEG_OPTIONS = {

        }

    # On ready
    @commands.Cog.listener()
    async def on_ready(self) -> None:
        for guild in self.client.guilds:
            id = int(guild.id)
            self.music_queue[id] = []
            self.queue_index[id] = 0
            self.voice_channel[id] = None
            self.is_playing[id] = self.is_paused[id] = False




    @app_commands.command(name="join")
    async def join_voice_channel(self, interaction: discord.Interaction) -> None:
        """ Joins the voice channel """
        self.voice_channel = interaction.user.voice.channel
        await self.voice_channel.connect()
        await interaction.response.send_message("Connected!", ephemeral=False)



    @app_commands.command(name="leave")
    async def leave_voice_channel(self, interaction: discord.Interaction) -> None:
        """ Leaves the voice channel """
        guild_id = interaction.guild.id
        voice_state = self.voice_channel[guild_id]

        # Check the state
        if voice_state is None:
            await interaction.response.send_message("Not connected to any voice channel.", ephemeral=False)
            return

        voice_client = await voice_state.connect()
        await voice_client.disconnect()
        self.voice_channel[guild_id] = None
        await interaction.response.send_message("Disconnected!", ephemeral=False)



    @app_commands.command(name="play")
    async def play(self, interaction: discord.Interaction) -> None:
        """ Plays a song """
        pass
    


    @app_commands.command(name="stop")
    async def stop(self, interaction: discord.Interaction) -> None:
        """ Stops playing """
        pass



    @app_commands.command(name="queue")
    async def queue(self, interaction: discord.Interaction) -> None:
        """ Displays the command queue """
        pass



async def setup(client: commands.Bot) -> None:
    try:
        await client.add_cog(Music(client))
        print ("[OK]")
    except:
        print ("[ERROR]")


