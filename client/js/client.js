// import WaveSurfer from 'wavesurfer.min.js';
import createVideoElement from './helpers/createVideoElement.js';
import removeVideoElements from './helpers/removeVideoElements.js';
import onDocumentReady from "./helpers/onDocumentReady";


/*
 * todo:
 *  - use browser video capture as input
 *  - use browser audio capture as input
 *  - use browser audio capture as input and visualize it
 *  - refactor the backend
 *  - process the video with OpenFace
 *      - option 1: collect individual frame data, append it to a data frame and render
 *      - option 2: process video segments and render each segment's data
 */
onDocumentReady(() => {
    let pc = null;
    let wavesurfer = null;
    let isRecording = false;

    const $videoTransform = document.getElementById('video-transform'),
        $useStun = document.getElementById('use-stun'),
        $start = document.getElementById('start'),
        $stop = document.getElementById('stop'),
        $audio = document.getElementById('audio'),
        $mediaContainer = document.getElementById("media"),
        $startStopButton = document.getElementById('startStopButton');

    window.app = {
        start() {
            const config = {
                sdpSemantics: 'unified-plan'
            };

            if ($useStun.checked) {
                config.iceServers = [{urls: ['stun:stun.l.google.com:19302']}];
            }

            pc = new RTCPeerConnection(config);

            // connect audio / video
            pc.addEventListener('track', function (evt) {
                console.log('track event', evt);

                if (evt.track.kind === 'video') {
                    createVideoElement(evt.track.id, new MediaStream([evt.track]), $mediaContainer);
                }

                if (evt.track.kind === 'audio') {
                    // createVideoElement(evt.track.id, new MediaStream([evt.track]));
                    $audio.srcObject = new MediaStream([evt.track]);

                    // Ensure the audio element has a valid src before loading it into WFPlayer
                    $audio.onloadedmetadata = () => {
                        // if (!audio.srcObject) {
                        //     console.error('Audio element does not have a valid srcObject');
                        //     return;
                        // }
                        //
                        // // if (!audio.src) {
                        // //     audio.src = URL.createObjectURL(audio.srcObject);
                        // // }
                        //
                        // const wf = new WFPlayer({
                        //     container: document.getElementById('waveform'),
                        //     mediaElement: audio,
                        // });
                        //
                        // wf.load(audio);

                        // createWaveSurfer(audio.srcObject);
                    };
                    // const wf = new WFPlayer({
                    //     container: document.getElementById('waveform'),
                    //     mediaElement: document.getElementById('audio'),
                    // });
                    //
                    // wf.load(document.getElementById('audio'));
                }

                // if (evt.track.label === 'processed_capture') {
                //     document.getElementById('processed_capture').srcObject = evt.streams[0];
                // } else {
                //     document.getElementById('unprocessed_capture').srcObject = evt.streams[0];
                // }
            });

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

            this.negotiate();

            // document.getElementById('start').style.display = 'none';
            // document.getElementById('stop').style.display = 'inline-block';
        },

        stop() {
            // document.getElementById('stop').style.display = 'none';
            // document.getElementById('start').style.display = 'inline-block';

            // close peer connection
            setTimeout(function () {
                pc.close();
                removeVideoElements($mediaContainer);
            }, 500);
        },

        async negotiate() {
            pc.addTransceiver('video', {direction: 'recvonly'});
            pc.addTransceiver('video', {direction: 'recvonly'});
            pc.addTransceiver('audio', {direction: 'recvonly'});

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
            // return pc.createOffer().then(function (offer) {
            //     return pc.setLocalDescription(offer);
            // }).then(function () {
            //     // wait for ICE gathering to complete
            //     return new Promise(function (resolve) {
            //         if (pc.iceGatheringState === 'complete') {
            //             resolve();
            //         } else {
            //             function checkState() {
            //                 if (pc.iceGatheringState === 'complete') {
            //                     pc.removeEventListener('icegatheringstatechange', checkState);
            //                     resolve();
            //                 }
            //             }
            //
            //             pc.addEventListener('icegatheringstatechange', checkState);
            //         }
            //     });
            // }).then(function () {
            //     const offer = pc.localDescription;
            //     return fetch('/offer', {
            //         body: JSON.stringify({
            //             sdp: offer.sdp,
            //             type: offer.type,
            //             video_transform: document.getElementById('video-transform').value
            //         }),
            //         headers: {
            //             'Content-Type': 'application/json'
            //         },
            //         method: 'POST'
            //     });
            // }).then(function (response) {
            //     return response.json();
            // }).then(function (answer) {
            //     return pc.setRemoteDescription(answer);
            // }).catch(function (e) {
            //     alert(e);
            // });
        },

        toggleStartStopButtonState() {
            isRecording = !isRecording;
            if (isRecording) {
                $startStopButton.innerText = "Stop";
                // $startStopButton.classList.remove('start-button');
                // $startStopButton.classList.add('stop-button');
            } else {
                $startStopButton.innerText = "Start";
                // $startStopButton.classList.remove('stop-button');
                // $startStopButton.classList.add('start-button');
            }
        }
    };

    $startStopButton.addEventListener('click', () => {
        if (isRecording) {
            app.stop();
        } else {
            app.start();
        }
        app.toggleStartStopButtonState();
    });

// var wavesurfer;
// var micContext;
// var mediaStreamSource;
// var levelChecker;
//
// const createWaveSurfer = async (audioStream) => {
//     // Create an instance of WaveSurfer
//     if (wavesurfer) {
//         wavesurfer.destroy()
//     }
//     wavesurfer = WaveSurfer.create({
//         container: '#mic',
//         waveColor: 'rgb(200, 0, 200)',
//         progressColor: 'rgb(100, 0, 100)',
//     })
//
//     try {
//         micContext = wavesurfer.backend.getAudioContext();
//         mediaStreamSource = micContext.createMediaStreamSource(stream);
//         levelChecker = micContext.createScriptProcessor(4096, 1, 1);
//
//         mediaStreamSource.connect(levelChecker);
//         levelChecker.connect(micContext.destination);
//
//         levelChecker.onaudioprocess = function (event) {
//             wavesurfer.empty();
//             wavesurfer.loadDecodedBuffer(event.inputBuffer);
//         };
//     } catch (error) {
//         console.error('Error decoding audio data:', error);
//     }
//
//     // // Initialize the Record plugin
//     // record = wavesurfer.registerPlugin(RecordPlugin.create({scrollingWaveform, renderRecordedAudio: false}))
//     // // Render recorded audio
//     // record.on('record-end', (blob) => {
//     //     const container = document.querySelector('#recordings')
//     //     const recordedUrl = URL.createObjectURL(blob)
//     //
//     //     // Create wavesurfer from the recorded audio
//     //     const wavesurfer = WaveSurfer.create({
//     //         container,
//     //         waveColor: 'rgb(200, 100, 0)',
//     //         progressColor: 'rgb(100, 50, 0)',
//     //         url: recordedUrl,
//     //     })
//     //
//     //     // Play button
//     //     const button = container.appendChild(document.createElement('button'))
//     //     button.textContent = 'Play'
//     //     button.onclick = () => wavesurfer.playPause()
//     //     wavesurfer.on('pause', () => (button.textContent = 'Play'))
//     //     wavesurfer.on('play', () => (button.textContent = 'Pause'))
//     //
//     //     // Download link
//     //     const link = container.appendChild(document.createElement('a'))
//     //     Object.assign(link, {
//     //         href: recordedUrl,
//     //         download: 'recording.' + blob.type.split(';')[0].split('/')[1] || 'webm',
//     //         textContent: 'Download recording',
//     //     })
//     // })
//     // pauseButton.style.display = 'none'
//     // recButton.textContent = 'Record'
//
//     // record.on('record-progress', (time) => {
//     //     updateProgress(time)
//     // })
// }

    function createWaveSurfer(stream) {
        if (wavesurfer) {
            wavesurfer.destroy();
        }

        wavesurfer = WaveSurfer.create({
            container: '#waveform',
            waveColor: 'violet',
            progressColor: 'purple',
            backend: 'WebAudio'
        });

        console.log('wavesurfer', wavesurfer);

        const audioContext = new (window.AudioContext || window.webkitAudioContext)();
        const mediaStreamSource = audioContext.createMediaStreamSource(stream);
        const analyser = audioContext.createAnalyser();

        mediaStreamSource.connect(analyser);

        const processAudio = () => {
            const bufferLength = analyser.frequencyBinCount;
            const dataArray = new Uint8Array(bufferLength);
            analyser.getByteTimeDomainData(dataArray);

            // Convert Uint8Array to Float32Array
            const float32Array = new Float32Array(bufferLength);
            for (let i = 0; i < bufferLength; i++) {
                float32Array[i] = (dataArray[i] - 128) / 128.0; // Convert to range [-1, 1]
            }

            const audioBuffer = audioContext.createBuffer(1, bufferLength, audioContext.sampleRate);
            audioBuffer.copyToChannel(float32Array, 0);

            wavesurfer.loadDecodedBuffer(audioBuffer);
            requestAnimationFrame(processAudio);
        };

        processAudio();
    }
});
