import { generateRequestHeaders } from './generateRequestHeaders.js';
import { wrapResponse } from './wrapResponse.js';

const clearAvailabilityTimeSlots = async ({ token }) => {
    const url = `/availabilities/${token}/slots/clear`;

    return wrapResponse(
        fetch(url, {
            method: 'POST',
            headers: generateRequestHeaders(),
        }),
    );
};

export { clearAvailabilityTimeSlots };
