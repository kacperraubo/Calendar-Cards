import { generateRequestHeaders } from './generateRequestHeaders.js';
import { json } from './utils.js';
import { wrapResponse } from './wrapResponse.js';

const editEvent = async ({
    title,
    description,
    guests,
    address,
    addedDates,
    deletedDates,
    startTime,
    endTime,
    section,
    reminders,
    token,
}) => {
    const url = `/events/${token}/edit`;

    return wrapResponse(
        fetch(url, {
            method: 'POST',
            headers: generateRequestHeaders(),
            body: json({
                title,
                description,
                guests,
                address,
                section,
                reminders,
                dates: addedDates,
                deleted_dates: deletedDates,
                start_time: startTime || null,
                end_time: endTime || null,
            }),
        }),
    );
};

export { editEvent };
