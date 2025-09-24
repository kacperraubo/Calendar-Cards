import { generateRequestHeaders } from './generateRequestHeaders.js';
import { json } from './utils.js';
import { wrapResponse } from './wrapResponse.js';

const editAcceptedInvitation = async ({ token, section, reminders }) => {
    const url = `/invitations/${token}/edit`;

    return wrapResponse(
        fetch(url, {
            method: 'POST',
            headers: generateRequestHeaders(),
            body: json({
                section,
                reminders,
            }),
        }),
    );
};

export { editAcceptedInvitation };
