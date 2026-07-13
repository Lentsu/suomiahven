# ensure_connected.py

import discord

from functools import wraps


def ensure_connected(func):
    """Ensure the bot is connected to user's voice channel"""
    @wraps(func)
    async def wrapper(self, interaction: discord.Interaction, *args, **kwargs):

        if interaction.guild is None:
            await interaction.response.send_message(
                "You are not on any server.", ephemeral=True
            )
            return

        if interaction.user.voice is None:
            await interaction.response.send_message(
                "You are not on any voice channel.", ephemeral=True
            )
            return

        # Get session from client.audio (AudioManager)
        session = self.client.audio.get_session(interaction.guild.id)

        await session.ensure_connected(interaction.user.voice.channel)

        return await func(self, interaction, *args, **kwargs)

    return wrapper

