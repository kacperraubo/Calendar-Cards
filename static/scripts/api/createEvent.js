import { generateRequestHeaders } from './generateRequestHeaders.js';
import { json } from './utils.js';
import { wrapResponse } from './wrapResponse.js';

const createEvent = async ({
    section,
    title,
    description,
    guests,
    address,
    dates,
    startTime,
    endTime,
    reminders,
}) => {
    const url = `/events/create`;

    return wrapResponse(
        fetch(url, {
            method: 'POST',
            headers: generateRequestHeaders(),
            body: json({
                section,
                title,
                description,
                guests,
                address,
                reminders,
                dates,
                start_time: startTime || null,
                end_time: endTime || null,
            }),
        }),
    );
};

export { createEvent };
