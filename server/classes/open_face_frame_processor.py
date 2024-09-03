import json
import tempfile
import cv2
import matplotlib.pyplot as plt
import os
import subprocess
import numpy as np
import pandas as pd
import seaborn as sns
import re

from aiortc import RTCPeerConnection, RTCDataChannel

from server.helpers.get_log_info import get_log_info

# Video recording parameters
OPEN_FACE_BINARIES_PATH = "/Users/iskandarr/Documents/Projects/_Community/fea_tool/external_libs/openFace/OpenFace/build/bin"
OPEN_FACE_FRAME_FILE = "frame.jpg"
OPEN_FACE_PROCESSED_FRAME_FILE = "frame_processed.jpg"
OPEN_FACE_EXTRACTED_FEATURES_FILE = 'frame_processed.csv'

TEMP_DIR = tempfile.mkdtemp()
print('TEMP_DIR', TEMP_DIR)


class OpenFaceFrameProcessor:
    data_channel = None

    def __init__(self, pc: RTCPeerConnection):
        # super().__init__()
        self.pc = pc

        log_info = get_log_info("OpenFaceFrameProcessor()")

        @pc.on("datachannel")
        async def on_datachannel(data_channel: RTCDataChannel):
            log_info("Data channel received %s", data_channel.label)

            if data_channel.label == "graphs":
                self.data_channel = data_channel

                data_channel.send("Hello World!")

    async def process_frame(self, frame):
        # Ensure the frame is a valid NumPy array with a supported data type
        if not isinstance(frame, np.ndarray):
            raise ValueError("Frame must be a NumPy array")

        # Ensure the frame is continuous
        if not hasattr(frame, 'flags') or not frame.flags['C_CONTIGUOUS']:
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

    async def collect_extracted_features(self):
        # Load data
        df = pd.read_csv(os.path.join(TEMP_DIR, OPEN_FACE_EXTRACTED_FEATURES_FILE))
        # Remove empty spaces in column names.
        df.columns = [col.replace(" ", "") for col in df.columns]

        # Threshold data by 80%
        df_clean = df[df.confidence >= .80]

        # Plot all Action Unit time series.
        au_regex_pat = re.compile(r'^AU[0-9]+_r$')
        au_columns = df.columns[df.columns.str.contains(au_regex_pat)]
        print("List of AU columns:", au_columns)

        if self.data_channel is not None:
            # serializable_data = au_columns.tolist()
            serializable_data = df_clean.to_dict()

            json_string = json.dumps(serializable_data)
            self.data_channel.send(json_string)

        # f, axes = plt.subplots(6, 3, figsize=(10, 12), sharex=True, sharey=True)
        # axes = axes.flatten()
        # for au_ix, au_col in enumerate(au_columns):
        #     sns.lineplot(x='frame', y=au_col, hue='face', data=df_clean, ax=axes[au_ix])
        #     axes[au_ix].set(title=au_col, ylabel='Intensity')
        #     axes[au_ix].legend(loc=5)
        # plt.suptitle("AU intensity predictions by time for each face", y=1.02)
        # plt.tight_layout()

        # Let's compare how much AU12 (smiling) activity occurs at similar times across people.
        # df_clean.pivot(index='frame', columns='face', values='AU12_r').corr()

    # def create_data_channel(self):
    #     # Create a data channel
    #     data_channel = self.pc.createDataChannel("graphs", negotiated=True, id=0)
    #
    #     # Set up event listeners for the data channel
    #     @data_channel.on("open")
    #     def on_data_channel_open():
    #         print("Data channel is open")
    #         # data_channel.send("Hello, World!")
    #
    #     @data_channel.on("message")
    #     def on_data_channel_message(message):
    #         print(f"Received message: {message}")
    #
    #     @data_channel.on("close")
    #     def on_datachannel_close():
    #         print("Data channel is closed")
    #
    #     self.data_channel = data_channel
