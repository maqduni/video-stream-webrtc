import asyncio
import fractions
import json
import logging
import os
import time
import uuid

import numpy as np
import pyaudio
from aiohttp import web
from aiortc import RTCPeerConnection, RTCSessionDescription, MediaStreamTrack
from av import AudioFrame

from server.open_cv_capture import OpenCVCapture

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

pcs = set()

ROOT = os.path.dirname(__file__)

# Audio stream parameters
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 44100
FRAMES_PER_BUFFER = 2048


class AudioCapture(MediaStreamTrack):
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


async def index(request):
    content = open(os.path.join(ROOT, "public/index.html"), "r").read()
    return web.Response(content_type="text/html", text=content)

# async def javascript(request):
#     content = open(os.path.join(ROOT, "public/client.js"), "r").read()
#     return web.Response(content_type="application/javascript", text=content)


async def offer(request):
    params = await request.json()
    offer = RTCSessionDescription(sdp=params["sdp"], type=params["type"])

    pc = RTCPeerConnection()
    pc_id = "PeerConnection(%s)" % uuid.uuid4()
    pcs.add(pc)

    def log_info(msg, *args):
        logger.info(pc_id + " " + msg, *args)

    log_info("Created for %s", request.remote)
    # player = MediaPlayer(os.path.join(ROOT, "sample.ts"))

    unprocessed_video_capture_track = OpenCVCapture(processed=False)
    pc.addTrack(unprocessed_video_capture_track)

    processed_video_capture_track = OpenCVCapture(processed=True)
    pc.addTrack(processed_video_capture_track)

    audio_capture_track = AudioCapture()
    pc.addTrack(audio_capture_track)

    @pc.on("connectionstatechange")
    async def on_connectionstatechange():
        log_info("Connection state is %s", pc.connectionState)
        if (pc.connectionState == "failed"
                or pc.connectionState == "closed"):
            await close_peer_connections(None)

    @pc.on("track")
    def on_track(track):
        log_info("Track %s received", track.kind)

        @track.on("ended")
        async def on_ended():
            log_info("Track %s ended", track.kind)

    # handle offer
    await pc.setRemoteDescription(offer)

    # send answer
    answer = await pc.createAnswer()
    await pc.setLocalDescription(answer)

    return web.Response(
        content_type="application/json",
        text=json.dumps(
            {"sdp": pc.localDescription.sdp, "type": pc.localDescription.type}
        ),
    )


async def close_peer_connections(app):
    # close peer connections
    coros = [pc.close() for pc in pcs]
    await asyncio.gather(*coros)
    pcs.clear()


if __name__ == "__main__":
    app = web.Application()
    app.on_shutdown.append(close_peer_connections)

    # Routes
    app.router.add_get("/", index)
    # app.router.add_get("/public/client.js", javascript)
    app.router.add_post("/offer", offer)
    app.router.add_static('/', path=os.path.join(ROOT, "public"), name='public')

    web.run_app(app, access_log=None, host="0.0.0.0", port=8080, ssl_context=None)
