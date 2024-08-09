#   template.py
import os

from discord.ext import commands
from discord import app_commands
import discord

from pydub import AudioSegment
import pyttsx3

# Import local auxillary functions
from cogs.auxillary import try_wrap
    
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

# Commands and events for greeting users
class Template(commands.Cog):
    
    # Suorittaa synkronisen funktion asynkronisesti
    return await asyncio.to_thread(synch_text_to_speech)

    def __init__(self, client) -> None:
        self.client = client
    
    @commands.command(name='puhu', help='Muuttaa annetun tekstin puheeksi ja toistaa sen äänikanavalla.')
    async def _puhu(self, ctx, *, teksti: str):
        if not ctx.message.author.voice:
            await ctx.send("Sinun täytyy olla äänikanavalla käyttääksesi tätä komentoa.")
            return

        # Join the voice channel if not already there
        if not ctx.voice_state.voice:
            await ctx.invoke(self._join)

        tts_filename = await async_text_to_speech(teksti)  # Muutettu käyttämään asynkronista versiota
        await ctx.voice_client.play(discord.FFmpegPCMAudio(executable=FFMPEG_EXECUTABLE, source=tts_filename), after=lambda e: print('TTS valmis.', e))

        # Tiedoston siivous
        os.remove(tts_filename)

    @app_commands.command(name="test")
    async def command(self, interaction: discord.Interaction) -> None:
        """ Command description for the autogenerated help function """
        await interaction.response.send_message("Interaction response", ephemeral=False)
    
    @_puhu.before_invoke
    async def ensure_voice_state(self, ctx: commands.Context):
        if not ctx.author.voice or not ctx.author.voice.channel:
            raise commands.CommandError('You are not connected to any voice channel.')

        if ctx.voice_client:
            if ctx.voice_client.channel != ctx.author.voice.channel:
                raise commands.CommandError('Bot is already in a voice channel.')

@try_wrap
async def setup(client: commands.Bot) -> None:
    """ Tries to load the Cog to the client and prints [OK] on success """
    await client.add_cog(Template(client))

