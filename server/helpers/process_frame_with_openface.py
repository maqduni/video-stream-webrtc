import tempfile
import os
import numpy as np
import cv2
import subprocess

# Video recording parameters
OPEN_FACE_BINARIES_PATH = "/Users/iskandarr/Documents/Projects/_Community/fea_tool/external_libs/openFace/OpenFace/build/bin"
OPEN_FACE_FRAME_FILE = "frame.jpg"
OPEN_FACE_PROCESSED_FRAME_FILE = "frame_processed.jpg"

TEMP_DIR = tempfile.mkdtemp()
print('TEMP_DIR', TEMP_DIR)

async def process_frame_with_openface(frame):
    # Ensure the frame is continuous
    if not frame.flags['C_CONTIGUOUS']:
        frame = np.ascontiguousarray(frame)

    frame_path = os.path.join(TEMP_DIR, OPEN_FACE_FRAME_FILE)
    cv2.imwrite(frame_path, frame)

    # Command to run OpenFace on the frame
    command = [
        f"{OPEN_FACE_BINARIES_PATH}/FaceLandmarkImg",
        "-f", frame_path,
        "-out_dir", TEMP_DIR,
        "-of", OPEN_FACE_PROCESSED_FRAME_FILE,
        # "-mloc", MODEL_LOCATION_PATH,
        # "-fd", HAAR_CASCADE_PATH,
        # "-eye_model", EYE_MODEL_PATH,
    ]

    try:
        subprocess.run(command, check=True)
    except subprocess.CalledProcessError as e:
        print(f"Error during FeatureExtraction: {e}")
        return None
    except Exception as e:
        print(f"Unexpected error: {e}")
        return None

    # Load the processed frame (assuming OpenFace outputs a processed image)
    processed_frame_path = os.path.join(TEMP_DIR, OPEN_FACE_PROCESSED_FRAME_FILE)
    # processed_frame_path = frame_path
    if not os.path.exists(processed_frame_path):
        print(f"Processed frame not found at {processed_frame_path}")
        return None

    processed_frame = cv2.imread(processed_frame_path)
    if processed_frame is None:
        print(f"Failed to read processed frame from {processed_frame_path}")
        return None

    return processed_frame
