from audio.session import AudioSession

class AudioManager:
    """Manages all per-guild AudioSessions"""

    def __init__(self):
        self._sessions: dict[int, AudioSession] = {}


    @property
    def sessions(self):
        """Get all AudioSessions"""
        return self._sessions.values()


    def get_session(self, guild_id: int) -> AudioSession:
        """Gets the AudioSession of a guild or creates one"""
        if guild_id not in self._sessions:
            self._sessions[guild_id] = AudioSession()
        return self._sessions[guild_id]


    def remove_session(self, guild_id: int) -> AudioSession | None:
        """Removes the AudioSession of a guild (if any) and return it"""
        self._sessions.pop(guild_id, None)


    async def cleanup(self):
        """Disconnect and remove idle sessions"""
        for guild_id, session in list(self._sessions.items()):
            if session.idle:
                await session.disconnect()
                self.remove_session(guild_id)
