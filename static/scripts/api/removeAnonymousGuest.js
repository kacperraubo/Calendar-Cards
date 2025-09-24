import { generateRequestHeaders } from './generateRequestHeaders.js';
import { wrapResponse } from './wrapResponse.js';

const removeAnonymousGuest = async ({ token, email }) => {
    const url = `/events/${token}/guests/${email}/remove`;

    return wrapResponse(
        fetch(url, {
            method: 'POST',
            headers: generateRequestHeaders(),
        }),
    );
};

export { removeAnonymousGuest };
