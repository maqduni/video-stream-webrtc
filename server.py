import asyncio
import fractions
import logging
import os
import uuid

import numpy as np
import pyaudio
from aiohttp import web
from aiortc import RTCPeerConnection, RTCSessionDescription, MediaStreamTrack, RTCIceCandidate
from av import AudioFrame

from server.helpers.parse_candidate import parse_candidate
from server.tracks.open_cv_process_track import OpenCVProcessTrack

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

pcs = set()

ROOT = os.path.dirname(__file__)


async def index(request):
    content = open(os.path.join(ROOT, "public/index.html"), "r").read()
    return web.Response(content_type="text/html", text=content)


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

    # unprocessed_video_capture_track = OpenCVCapture(processed=False)
    # pc.addTrack(unprocessed_video_capture_track)
    #
    # processed_video_capture_track = OpenCVCapture(processed=True)
    # pc.addTrack(processed_video_capture_track)
    #
    # audio_capture_track = AudioCapture()
    # pc.addTrack(audio_capture_track)

    @pc.on("connectionstatechange")
    async def on_connectionstatechange():
        log_info("Connection state is %s", pc.connectionState)
        if pc.connectionState in ["failed", "closed", "disconnected"]:
            await close_peer_connections(None)
        elif pc.connectionState == "consent_expired":
            await close_peer_connections(None)

    # @pc.on('icecandidate')
    # async def on_icecandidate(candidate):
    #     log_info("ICE candidate received", candidate)
    #     # await request.app['websockets'].send_json({'candidate': candidate})

    @pc.on("track")
    def on_track(track):
        log_info("Track %s received", track.kind)

        if track.kind == "video":
            local_video = OpenCVProcessTrack(track)
            pc.addTrack(local_video)

        @track.on("ended")
        async def on_ended():
            log_info("Track %s ended", track.kind)

    # handle offer
    await pc.setRemoteDescription(offer)

    # send answer
    answer = await pc.createAnswer()
    await pc.setLocalDescription(answer)

    return web.json_response({'sdp': pc.localDescription.sdp, 'type': pc.localDescription.type})


async def ice_candidate(request):
    params = await request.json()
    candidate_param = parse_candidate(params['candidate'])

    candidate = RTCIceCandidate(sdpMid=params['sdpMid'],
                                sdpMLineIndex=params['sdpMLineIndex'],
                                component=candidate_param['component'],
                                foundation=candidate_param['foundation'],
                                ip=candidate_param['ip'],
                                port=candidate_param['port'],
                                priority=candidate_param['priority'],
                                protocol=candidate_param['protocol'],
                                tcpType=candidate_param['tcpType'],
                                type=candidate_param['type'],
                                )
    for pc in pcs:
        await pc.addIceCandidate(candidate)
    return web.Response()


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
    # app.router.add_post('/ice-candidate', ice_candidate)

    app.router.add_static('/', path=os.path.join(ROOT, "public"), name='public')

    web.run_app(app, access_log=None, host="0.0.0.0", port=8080, ssl_context=None)
