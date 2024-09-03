# Audio stream parameters
import fractions

import numpy as np
import pyaudio
from aiortc import MediaStreamTrack
from av import AudioFrame

FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 44100
FRAMES_PER_BUFFER = 2048


class AudioCaptureTrack(MediaStreamTrack):
    """
    An audio stream track that captures audion chunks.
    """

    kind = "audio"

    _timestamp = 0

    def __init__(self):
        super().__init__()  # don't forget this!

        # Initialize PyAudio
        self.port_audio = pyaudio.PyAudio()

        # Open audio stream
        self.stream = self.port_audio.open(format=FORMAT, channels=CHANNELS, rate=RATE, input=True,
                                           frames_per_buffer=FRAMES_PER_BUFFER)

    @property
    def audio(self):
        return self

    async def recv(self):
        data = self.stream.read(FRAMES_PER_BUFFER)
        audio_data = np.frombuffer(data, dtype=np.int16).reshape(-1, 1)

        frame = AudioFrame.from_ndarray(audio_data.T, format="s16", layout="stereo" if CHANNELS == 2 else "mono")

        frame.sample_rate = RATE
        frame.time_base = fractions.Fraction(1, RATE)

        self._timestamp += FRAMES_PER_BUFFER
        frame.pts = self._timestamp

        return frame

    def __del__(self):
        self.stream.stop_stream()
        self.stream.close()
        self.port_audio.terminate()
