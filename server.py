import asyncio
import os
import uuid
import ssl

from aiohttp import web
from aiortc import RTCPeerConnection, RTCSessionDescription, RTCIceCandidate, RTCDataChannel
from dotenv import load_dotenv

from server.helpers.get_log_info import get_log_info
from server.tracks.open_cv_process_track import OpenCVProcessTrack

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

    log_info = get_log_info(pc_id)

    log_info("Created for %s", request.remote)

    # Create a data channel
    # data_channel = pc.createDataChannel("graphs", negotiated=True, id=0)

    # Set up event listeners for the data channel
    # @data_channel.on("open")
    # def on_data_channel_open():
    #     print("Data channel is open")
    #     # data_channel.send("Hello, World!")
    #
    # @data_channel.on("message")
    # def on_data_channel_message(message):
    #     print(f"Received message: {message}")
    #
    # @data_channel.on("close")
    # def on_datachannel_close():
    #     print("Data channel is closed")

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
            local_video = OpenCVProcessTrack(track, pc)
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


# async def ice_candidate(request):
#     params = await request.json()
#     candidate_param = parse_candidate(params['candidate'])
#
#     candidate = RTCIceCandidate(sdpMid=params['sdpMid'],
#                                 sdpMLineIndex=params['sdpMLineIndex'],
#                                 component=candidate_param['component'],
#                                 foundation=candidate_param['foundation'],
#                                 ip=candidate_param['ip'],
#                                 port=candidate_param['port'],
#                                 priority=candidate_param['priority'],
#                                 protocol=candidate_param['protocol'],
#                                 tcpType=candidate_param['tcpType'],
#                                 type=candidate_param['type'],
#                                 )
#     for pc in pcs:
#         await pc.addIceCandidate(candidate)
#     return web.Response()


async def close_peer_connections(app):
    # close peer connections
    coros = [pc.close() for pc in pcs]
    await asyncio.gather(*coros)
    pcs.clear()

# Create an SSL context
ssl_context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
ssl_context.load_cert_chain('./server/server.crt', './server/server.key')

if __name__ == "__main__":
    load_dotenv()

    app = web.Application()
    app.on_shutdown.append(close_peer_connections)

    # Routes
    app.router.add_get("/", index)
    app.router.add_post("/offer", offer)
    # app.router.add_post('/ice-candidate', ice_candidate)

    app.router.add_static('/', path=os.path.join(ROOT, "public"), name='public')

    web.run_app(app, access_log=None, port=443, ssl_context=ssl_context)
