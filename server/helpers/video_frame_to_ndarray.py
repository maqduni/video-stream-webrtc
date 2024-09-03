import numpy as np
from av import VideoFrame


def video_frame_to_ndarray(frame: VideoFrame) -> np.ndarray:
    # Convert VideoFrame to ndarray
    return frame.to_ndarray(format='bgr24')
