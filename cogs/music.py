#   music.py

import discord
from discord import app_commands
from discord.ext import commands
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import os

class Music(commands.Cog):

    def __init__(self, client):
        self.client = client
        self.api_key = os.getenv('AIzaSyAXe3Zmfy4PHfio7KPbnQ55bCzkUT4mbxM')

    @commands.command()
    async def play(self, ctx, link):
        # Tarkista, että komennon lähettäjä on äänikanavalla
        if ctx.author.voice is None:
            await ctx.send("Sinun täytyy olla äänikanavalla käyttääksesi tätä komentoa.")
            return

        # Liity käyttäjän äänikanavalle
        voice_channel = ctx.author.voice.channel
        voice_client = await voice_channel.connect()

        # Tarkista, että botilla ei ole joista soittamassa
        if voice_client.is_playing():
            await ctx.send("Jo toistetaan musiikkia. Odota, että nykyinen kappale päättyy.")
            return

        #TODO

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

