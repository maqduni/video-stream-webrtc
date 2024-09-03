import fractions
import time

import cv2
from aiortc import MediaStreamTrack, RTCPeerConnection, RTCDataChannel

from server.classes.open_face_frame_processor import OpenFaceFrameProcessor
from server.helpers.get_log_info import get_log_info
from server.helpers.ndarray_to_video_frame import ndarray_to_video_frame
from server.helpers.video_frame_to_ndarray import video_frame_to_ndarray

SAMPLING_RATE = 15


class OpenCVProcessTrack(MediaStreamTrack):
    """
    A video stream track that captures frames from OpenCV.
    """

    kind = "video"

    sampled_frame = None
    sampling_step = 0

    def __init__(self, track: MediaStreamTrack, pc: RTCPeerConnection):
        super().__init__()
        self.track = track
        self.pc = pc
        self.frame_processor = OpenFaceFrameProcessor(pc)

    async def recv(self):
        frame = await self.track.recv()
        frame = video_frame_to_ndarray(frame)

        if self.sampled_frame is not None and not self.can_sample():
            return self.sampled_frame

        # Process the frame (e.g., apply transformations)
        frame = await self.frame_processor.process_frame(frame)
        await self.frame_processor.collect_extracted_features()

        frame = cv2.flip(frame, 1)

        self.sampled_frame = ndarray_to_video_frame(frame,
                                                    int(time.time() * 1000000),
                                                    fractions.Fraction(1, 1000000))
        return self.sampled_frame

    def can_sample(self):
        self.sampling_step += 1
        # print('sampling_step', self.sampling_step)

        if self.sampling_step % SAMPLING_RATE == 0:
            return True

        return False
