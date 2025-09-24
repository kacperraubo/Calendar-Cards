import { generateRequestHeaders } from './generateRequestHeaders.js';
import { wrapResponse } from './wrapResponse.js';

const deleteAvailabilityEvent = async ({ token }) => {
    const url = `/availabilities/events/${token}/delete`;

    return wrapResponse(
        fetch(url, {
            method: 'POST',
            headers: generateRequestHeaders(),
        }),
    );
};

export { deleteAvailabilityEvent };
