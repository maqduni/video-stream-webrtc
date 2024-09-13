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
from io import BytesIO

from aiortc import RTCPeerConnection, RTCDataChannel

from server.helpers.get_log_info import get_log_info

# Video recording parameters
OPEN_FACE_FRAME_FILE = "frame.jpg"
OPEN_FACE_PROCESSED_FRAME_FILE = "frame_processed.jpg"
OPEN_FACE_EXTRACTED_FEATURES_FILE = 'frame_processed.csv'

TEMP_DIR = tempfile.mkdtemp()
print('TEMP_DIR', TEMP_DIR)

DF_COLUMNS = ['AU01_r', 'AU02_r', 'AU04_r', 'AU05_r', 'AU06_r', 'AU07_r', 'AU09_r',
              'AU10_r', 'AU12_r', 'AU14_r', 'AU15_r', 'AU17_r', 'AU20_r', 'AU23_r',
              'AU25_r', 'AU26_r', 'AU45_r']

DF_COLUMN_LABELS = ['Inner brow raiser', 'Outer brow raiser', 'Brow lowerer', 'Upper lid raiser', 'Cheek raiser',
                    'Lid tightener', 'Nose wrinkler', 'Upper lip raiser',
                    'Lip corner puller', 'Dimpler', 'Lip corner depressor', 'Chin raiser', 'Lip stretcher',
                    'Lip tightener', 'Lips part', 'Jaw drop', 'Blink', ]


class OpenFaceFrameProcessor:
    data_channel = None
    df = None

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
            f"{os.getenv('OPEN_FACE_BINARIES_PATH')}/FaceLandmarkImg",
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
        # au_regex_pat = re.compile(r'^AU[0-9]+_r$')
        # au_columns = df.columns[df.columns.str.contains(au_regex_pat)]
        # print("List of AU columns:", au_columns)

        self.add_row_to_df(df_clean)

        self.send_graphs_to_client()

    def send_graphs_to_client(self):
        if self.data_channel is None:
            return

        f, axes = plt.subplots(6, 3, figsize=(10, 12), sharex=True, sharey=True)
        axes = axes.flatten()
        for au_ix, au_col in enumerate(DF_COLUMNS):
            sns.lineplot(x='frame', y=au_col, hue='face', data=self.df, ax=axes[au_ix])
            axes[au_ix].set(title=DF_COLUMN_LABELS[au_ix], ylabel='Intensity')
            axes[au_ix].legend(loc=5)
        plt.suptitle("AU intensity predictions by time for each face", y=1.02)
        plt.tight_layout()

        buffer = BytesIO()
        plt.savefig(buffer, format='png')
        buffer.seek(0)

        self.data_channel.send(buffer.read())

        # Send the DataFrame to the client
        # self.data_channel.send(json.dumps(self.df.to_dict(orient='records')))

        # # Let's compare how much AU12 (smiling) activity occurs at similar times across people.
        # df_clean.pivot(index='index', columns='face', values='AU12_r').corr()

    def add_row_to_df(self, row):
        # Create a new DataFrame with 30 rows
        if self.df is None:
            self.df = pd.DataFrame(0, index=range(30), columns=DF_COLUMNS + ['face', 'frame'])

        # Append df_clean to dummy_df
        combined_df = pd.concat([self.df, row], ignore_index=True)

        # Ensure the combined DataFrame only contains 30 rows
        if len(combined_df) > 30:
            combined_df = combined_df.iloc[-30:]

        # Reset the index
        combined_df = combined_df.reset_index(drop=True)

        # Copy index values to frame
        combined_df['frame'] = combined_df.index

        self.df = combined_df
