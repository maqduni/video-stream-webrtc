from av import VideoFrame


def ndarray_to_video_frame(img, pts, time_base):
    # rebuild a VideoFrame, preserving timing information
    new_frame = VideoFrame.from_ndarray(img, format="bgr24")

    new_frame.pts = pts
    new_frame.time_base = time_base

    return new_frame
