## Description
A simple example of using webrtc to stream video from server (PYTHON) to client browser (JS).

## Installation
1. update `OPEN_FACE_BINARIES_PATH` to point to the location of the OpenFace binary files 
2. run `> pip install -r requirements.txt`
3. run `> python server.py`

## To use .TS files
Use the following to convert .mp4 to .ts:

`ffmpeg -i abc.mp4 -c:v libx264 -c:a aac -b:a 160k -bsf:v h264_mp4toannexb -f mpegts -crf 32 pqr.ts`

No need of conversion to try out the example. Added just in case.
