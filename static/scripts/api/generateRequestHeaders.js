import { getCsrfToken } from '../utilities/csrf.js';

const generateRequestHeaders = ({
    accept = -1,
    contentType = -1,
    csrfToken = getCsrfToken(),
    ...dict
} = {}) => {
    if (accept === -1) {
        accept = 'application/json';
    }

    if (contentType === -1) {
        contentType = 'application/json';
    } else if (contentType === null) {
        contentType = undefined;
    }

    const headers = {
        Accept: accept,
        'X-CSRFToken': csrfToken,
        ...dict,
    };

    if (contentType !== undefined) {
        headers['Content-Type'] = contentType;
    }

    return headers;
};

export { generateRequestHeaders };
