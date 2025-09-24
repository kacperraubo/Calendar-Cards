import { generateRequestHeaders } from './generateRequestHeaders.js';
import { json } from './utils.js';
import { wrapResponse } from './wrapResponse.js';

const createEventForAvailability = async ({
    token,
    title,
    description,
    email,
    address,
    startTime,
    endTime,
}) => {
    const url = `/external/availability/${token}`;

    return wrapResponse(
        fetch(url, {
            method: 'POST',
            headers: generateRequestHeaders(),
            body: json({
                title,
                description,
                email,
                address,
                start_time: startTime || null,
                end_time: endTime || null,
            }),
        }),
    );
};

export { createEventForAvailability };
