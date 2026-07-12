import numpy as np
from collections.abc import Iterable
from audio.channel import AudioChannel

# Some precalculated constants for 20ms @ 48kHz PCM audio frames
SAMPLE_RATE     = 48000
FRAME_DURATION  = 0.020
CHANNELS        = 2
FRAME_SAMPLES   = int(SAMPLE_RATE * CHANNELS * FRAME_DURATION)
FRAME_BYTES     = 2 * FRAME_SAMPLES
EMPTY_FRAME     = b"\x00" * FRAME_BYTES

class AudioMixer():
    """Audio Mixer for mixing AudioSources"""

    def __init__(self):
        self.channels: dict[str, AudioChannel] = {}
        # Mixing and output buffers to reduce allocation overhead
        self._mix_buf = np.zeros(FRAME_SAMPLES, dtype=np.int32)
        self._out_buf = np.zeros(FRAME_SAMPLES, dtype=np.int16)


    def add_channel(self, name: str, channel: AudioChannel):
        """Register the audio channel {name, channel}"""
        self.channels[name] = channel


    def mix(self, frames: Iterable[bytes | None]) -> bytes:
        """Mix the given frames together"""
        self._mix_buf.fill(0)

        # Mixing is active if mixer has frames
        active = False

        # Mix frames
        for frame in frames:
            if frame is None:
                continue
            active = True
            self._mix_buf += np.frombuffer(frame, dtype=np.int16)

        if not active:
            return EMPTY_FRAME

        # Clip to 16-bit range and copy to output buffer
        np.clip(self._mix_buf, -32768, 32767, out=self._mix_buf)
        np.copyto(self._out_buf, self._mix_buf, casting="unsafe")

        return self._out_buf.tobytes()


    def read(self) -> bytes:
        """Reads and mixes the next 20ms frame (if any)"""
        return self.mix(
            channel.read()
            for channel in self.channels.values()
        )


    @property
    def finished(self) -> bool:
        """Returns True if the Mixer is completely empty"""
        return all(channel.finished for channel in self.channels.values())

