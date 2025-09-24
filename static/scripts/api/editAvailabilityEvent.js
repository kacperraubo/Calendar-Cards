import { generateRequestHeaders } from './generateRequestHeaders.js';
import { json } from './utils.js';
import { wrapResponse } from './wrapResponse.js';

const editAvailabilityEvent = async ({ token, reminders }) => {
    const url = `/availabilities/events/${token}/edit`;

    return wrapResponse(
        fetch(url, {
            method: 'POST',
            headers: generateRequestHeaders(),
            body: json({
                reminders,
            }),
        }),
    );
};

export { editAvailabilityEvent };
