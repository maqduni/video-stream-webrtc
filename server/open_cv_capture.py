import fractions
import time

import cv2
from aiortc import MediaStreamTrack

from server.helpers.image_to_video_frame import image_to_video_frame
from server.helpers.process_frame_with_openface import process_frame_with_openface


class OpenCVCapture(MediaStreamTrack):
    """
    A video stream track that captures frames from OpenCV.
    """

    kind = "video"

    def __init__(self, processed):
        super().__init__()  # don't forget this!
        self.cap = cv2.VideoCapture(0)
        self.processed = processed

    @property
    def video(self):
        return self

    async def recv(self):
        # Capture frame-by-frame
        ret, frame = self.cap.read()
        if not ret:
            raise RuntimeError("Failed to capture image")

        if self.processed:
            frame = await process_frame_with_openface(frame)

        frame = cv2.flip(frame, 1)

        return image_to_video_frame(frame,
                                    int(time.time() * 1000000),
                                    fractions.Fraction(1, 1000000))

    def __del__(self):
        self.cap.release()
