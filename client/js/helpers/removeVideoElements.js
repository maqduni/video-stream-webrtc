export default function removeVideoElements($mediaContainer) {
    while ($mediaContainer.firstChild) {
        $mediaContainer.firstChild.srcObject = null;
        $mediaContainer.removeChild($mediaContainer.firstChild);
    }
}
