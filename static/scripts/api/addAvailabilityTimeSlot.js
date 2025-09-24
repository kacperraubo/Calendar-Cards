import { generateRequestHeaders } from './generateRequestHeaders.js';
import { json } from './utils.js';
import { wrapResponse } from './wrapResponse.js';

const addAvailabilityTimeSlot = async ({
    section,
    date,
    startTime,
    endTime,
}) => {
    const url = `/availabilities/${date}/add`;

    return wrapResponse(
        fetch(url, {
            method: 'POST',
            headers: generateRequestHeaders(),
            body: json({
                section,
                start_time: startTime,
                end_time: endTime,
            }),
        }),
    );
};

export { addAvailabilityTimeSlot };
