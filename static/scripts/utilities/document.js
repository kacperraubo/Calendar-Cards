/**
 * @param {function} callback
 */
const onDocumentLoad = (callback) => {
    if (document.readyState === 'complete') {
        callback();
    } else {
        document.addEventListener('DOMContentLoaded', callback);
    }
};

const onClickOutside = (element, callback, once = true) => {
    const listener = (event) => {
        if (!element.contains(event.target)) {
            callback();

            if (once) {
                document.removeEventListener('click', listener);
            }
        }
    };

    document.addEventListener('click', listener);

    return listener;
};

const tick = async () => {
    return new Promise((resolve) => {
        setTimeout(resolve, 0);
    });
};

export { onDocumentLoad, onClickOutside, tick };
