## Description
A simple example of using webrtc to stream video from server (PYTHON) to client browser (JS).

## Installation
1. install OpenFace, [MacOS](https://pranav-srivastava.medium.com/openface-2-0-mac-installation-and-pose-detection-257289cbc79b), [Ubuntu](https://github.com/TadasBaltrusaitis/OpenFace/wiki/Unix-Installation)
2. update `OPEN_FACE_BINARIES_PATH` to point to the location of the OpenFace binary files 
2. run `> pip install -r requirements.txt`
3. run `> python server.py`

## To use .TS files
Use the following to convert .mp4 to .ts:

`ffmpeg -i abc.mp4 -c:v libx264 -c:a aac -b:a 160k -bsf:v h264_mp4toannexb -f mpegts -crf 32 pqr.ts`

No need of conversion to try out the example. Added just in case.

## Troubleshooting
1. On Ubuntu you might need to run `sudo apt-get install portaudio19-dev python3-dev` to install the required dependencies for pyaudio.
2. 