import { generateRequestHeaders } from './generateRequestHeaders.js';
import { wrapResponse } from './wrapResponse.js';

const removeAvailabilityTimeSlot = async ({ token }) => {
    const url = `/availabilities/slots/${token}/remove`;

    return wrapResponse(
        fetch(url, {
            method: 'POST',
            headers: generateRequestHeaders(),
        }),
    );
};

export { removeAvailabilityTimeSlot };
