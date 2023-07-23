#   music.py

import discord
import youtube_dl
from discord import app_commands
from discord.ext import commands
import os

# YTDL options
ytdl_format_options = {
    'format': 'bestaudio/best',
    'outtmpl': '%(extractor)s-%(id)s-%(title)s.%(ext)s',
    'restrictfilenames': True,
    'noplaylist': True,
    'nocheckcertificate': True,
    'ignoreerrors': False,
    'logtostderr': False,
    'quiet': True,
    'no_warnings': True,
    'default_search': 'auto',
    'source_address': '0.0.0.0' # bind to ipv4 since ipv6 addresses cause issues sometimes
}

# FFMPG options
ffmpeg_options = {
    'options': '-vn'
}

# Create a ytdl instance with format options
ytdl = youtube_dl.YoutubeDL(ytdl_format_options)

# YTDL Source class to interface with Cog class
class YTDLSource (discord.PCMVolumeTransformer):

    def __init__(self, source, *, data, volume=0.5):
        super().__init__(source, volume)

        self.data = data
        self.title = data.get('title')
        self.url = data.get('url')

    @classmethod
    async def from_url(cls, url, *, loop=None, stream=False):
        loop = 


# Cog class to interface with bot client
class Music(commands.Cog):

    def __init__(self, client):
        self.client = client

    @app_commands.command()
    async def play(self, interaction: discord.Interaction, search):
        
        # Check if the caller is on voice channel
        if (!interaction.member.voice.channel)
            await interaction.response.send_message("User not on voice channel!")
            return

        # Join the voice channel
        voice_channel = interaction.member.voice.channel
        voice_client = await voice_channel.connect()

        # Check if nothing is currently playing
        if voice_client.is_playing():
            # TODO: Add the 
            return

    @commands.command()
    async def stop(self, ctx):
        # Tarkista, että botilla on ääniyhteys
        if ctx.voice_client is None:
            await ctx.send("En ole liittynyt äänikanavalle.")
            return

        # Lopeta musiikin toistaminen ja poistu äänikanavasta
        ctx.voice_client.stop()
        await ctx.voice_client.disconnect()
        await ctx.send("Musiikin toisto on lopetettu ja olen poistunut äänikanavalta.")



async def setup(client) -> None:
    try:
        await client.add_cog(Music(client))
        print ("[OK]")
    except:
        print ("[ERROR]")

