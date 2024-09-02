export default function onDocumentReady(fn, context) {
    function onReady(event) {
        document.removeEventListener('DOMContentLoaded', onReady);
        fn.call(context || window, event);
    }

    function onReadyIe(event) {
        if (document.readyState === 'complete') {
            document.detachEvent('onreadystatechange', onReadyIe);
            fn.call(context || window, event);
        }
    }

    document.addEventListener && document.addEventListener('DOMContentLoaded', onReady) ||
    document.attachEvent      && document.attachEvent('onreadystatechange', onReadyIe);
}
