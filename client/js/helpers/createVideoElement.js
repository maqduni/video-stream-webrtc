export default function createVideoElement(id, srcObject, $mediaContainer) {
    const video = document.createElement('video');
    video.id = id;
    video.autoplay = true;
    video.playsInline = true;
    video.controls = true;
    video.srcObject = srcObject;

    $mediaContainer.appendChild(video);
}
