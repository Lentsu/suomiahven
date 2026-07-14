# song.py

import discord

from .ytdl_source import YTDLSource

from audio.playback_item import PlaybackItem


class Song(PlaybackItem):
    """Class to abstract YTDLSources to playback items"""

    __slots__ = ('source', 'requester')


    def __init__(self, source: YTDLSource, requester: discord.Member):
        self.source = source
        self.requester = requester


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
