import WaveSurfer from 'wavesurfer.js'
import RecordPlugin from 'wavesurfer.js/dist/plugins/record.esm.js'
import onDocumentReady from "./helpers/onDocumentReady";


/*
 * todo:
 *  - process the video with OpenFace
 *      - option 1: collect individual frame data, append it to a data frame and render
 *      - option 2: process video segments and render each segment's data
 */
onDocumentReady(() => {
    let pc = null;
    let wavesurfer = null;
    let record = null;
    let isRecording = false;
    let stream = null;

    const $videoTransform = document.getElementById('video-transform'),
        $useStun = document.getElementById('use-stun'),
        $audio = document.getElementById('audio'),
        $sourceVideo = document.getElementById('source-video'),
        $processedVideo = document.getElementById('processed-video'),
        $mediaContainer = document.getElementById("media"),
        $startStopButton = document.getElementById('start-stop-button'),
        $sourceAudio = document.getElementById('source-audio'),
        $waveForm = document.getElementById('waveform');

    window.app = {
        createMultipleDataChannels() {
            // // Create multiple data channels
            // let dataChannel1 = pc.createDataChannel("channel1");
            // let dataChannel2 = pc.createDataChannel("channel2");
            //
            // // Set up event listeners for dataChannel1
            // dataChannel1.onopen = () => {
            //     console.log("Data Channel 1 Opened");
            // };
            // dataChannel1.onclose = () => {
            //     console.log("Data Channel 1 Closed");
            // };
            // dataChannel1.onmessage = (event) => {
            //     console.log("Data Channel 1 Message:", event.data);
            // };
            //
            // // Set up event listeners for dataChannel2
            // dataChannel2.onopen = () => {
            //     console.log("Data Channel 2 Opened");
            // };
            // dataChannel2.onclose = () => {
            //     console.log("Data Channel 2 Closed");
            // };
            // dataChannel2.onmessage = (event) => {
            //     console.log("Data Channel 2 Message:", event.data);
            // };
        },

        async startPC() {
            const pcConfig = {
                sdpSemantics: 'unified-plan',
                // iceServers: [{urls: ['stun:stun.l.google.com:19302']}],
            };

            // if ($useStun.checked) {
            //     pcConfig.iceServers = [{urls: ['stun:stun.l.google.com:19302']}];
            // }

            pc = new RTCPeerConnection(pcConfig);

            // Receive audio / video tracks
            pc.addEventListener('track', function (event) {
                console.log('track event', event);

                if (event.track.kind === 'video') {
                    // createVideoElement(event.track.id, new MediaStream([event.track]), $mediaContainer);
                    $processedVideo.srcObject = new MediaStream([event.track]);
                }

                // if (event.track.kind === 'audio') {
                //     // createVideoElement(event.track.id, new MediaStream([event.track]));
                //     $audio.srcObject = new MediaStream([event.track]);
                //
                //     // Ensure the audio element has a valid src before loading it into WFPlayer
                //     $audio.onloadedmetadata = () => {
                //
                //     };
                // }
            });

            // pc.addEventListener('icecandidateerror', event => {
            //     console.log('icecandidateerror', event);
            // })
            //
            // pc.addEventListener('icecandidate', event => {
            //     console.log('icecandidate event', event);
            //
            //     pc.addIceCandidate(event.candidate);
            //
            //     if (event.candidate) {
            //         // Send the ICE candidate to the backend
            //         fetch('/ice-candidate', {
            //             method: 'POST',
            //             headers: {'Content-Type': 'application/json'},
            //             body: JSON.stringify(event.candidate)
            //         });
            //     }
            // });

            if (navigator.mediaDevices && navigator.mediaDevices.getUserMedia) {
                try {
                    stream = await navigator.mediaDevices.getUserMedia({
                        video: true,
                        audio: true
                    });
                    console.log(stream);

                    /*
                     * Video
                     */
                    $sourceVideo.srcObject = stream;
                    $sourceVideo.muted = true;
                    stream.getVideoTracks().forEach(track => pc.addTrack(track, stream));

                    /*
                     * Audio
                     */
                    $sourceAudio.srcObject = stream;
                    $sourceAudio.muted = true;
                } catch (err) {
                    console.error('Error accessing media devices.', err);
                }
            } else {
                console.error('getUserMedia is not supported in this browser.');
            }

            this.negotiatePC();
        },

        stopPC() {
            // close peer connection
            setTimeout(function () {
                if (pc) {
                    pc.close();
                    // removeVideoElements($mediaContainer);
                    $processedVideo.srcObject = null;
                }

                if (stream) {
                    const tracks = stream.getTracks();
                    tracks.forEach(track => track.stop());

                    $sourceVideo.srcObject = null;
                }

                app.stopWaveSurfer();
            }, 500);
        },

        async negotiatePC() {
            /*
             * type RTCRtpTransceiverDirection = "inactive" | "recvonly" | "sendonly" | "sendrecv" | "stopped";
             */
            // pc.addTransceiver('video', {direction: 'recvonly'});
            // pc.addTransceiver('video', {direction: 'sendrecv'});

            try {
                const offer = await pc.createOffer();
                await pc.setLocalDescription(offer);

                await new Promise(function (resolve) {
                    if (pc.iceGatheringState === 'complete') {
                        resolve();
                    } else {
                        function checkState() {
                            if (pc.iceGatheringState === 'complete') {
                                pc.removeEventListener('icegatheringstatechange', checkState);
                                resolve();
                            }
                        }

                        pc.addEventListener('icegatheringstatechange', checkState);
                    }
                });

                const sessionDescription = pc.localDescription;
                console.log('sessionDescription', sessionDescription);

                const response = await fetch('/offer', {
                    body: JSON.stringify({
                        sdp: sessionDescription.sdp,
                        type: sessionDescription.type,
                        video_transform: $videoTransform.value
                    }),
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    method: 'POST'
                });

                const answer = await response.json();
                await pc.setRemoteDescription(answer);

            } catch (error) {
                console.error(error);
            }
        },

        toggleStartStopButtonState() {
            isRecording = !isRecording;
            if (isRecording) {
                $startStopButton.innerText = "Stop";
            } else {
                $startStopButton.innerText = "Start";
            }
        },

        async startWaveSurfer() {
            // Create an instance of WaveSurfer
            if (wavesurfer) {
                wavesurfer.destroy()
            }
            wavesurfer = WaveSurfer.create({
                container: '#waveform',
                waveColor: 'rgb(200, 0, 200)',
                progressColor: 'rgb(100, 0, 100)',
            })

            // console.log('RecordPlugin.getAvailableAudioDevices()', RecordPlugin.getAvailableAudioDevices());

            const deviceId = (await RecordPlugin.getAvailableAudioDevices())[0].deviceId;

            // Initialize the Record plugin
            record = wavesurfer.registerPlugin(RecordPlugin.create({
                scrollingWaveform: true,
                renderRecordedAudio: false
            }))
            record.startRecording({deviceId}).then(() => {
            })

            // Render recorded audio
            record.on('record-end', (blob) => {
            });
            record.on('record-progress', (time) => {
            })
        },
        stopWaveSurfer() {
            if (record.isRecording() || record.isPaused()) {
                record.stopRecording();
            }
        },
    };

    $startStopButton.addEventListener('click', () => {
        if (isRecording) {
            app.stopPC();
        } else {
            app.startPC();
        }
        app.toggleStartStopButtonState();
    });

    $sourceAudio.onloadedmetadata = () => {
        app.startWaveSurfer();
    };
});
