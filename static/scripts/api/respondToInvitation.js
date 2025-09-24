import { generateRequestHeaders } from './generateRequestHeaders.js';
import { json } from './utils.js';
import { wrapResponse } from './wrapResponse.js';

const respondToInvitation = async ({ token, accept, section }) => {
    const url = `/invitations/${token}/respond`;

    return wrapResponse(
        fetch(url, {
            method: 'POST',
            headers: generateRequestHeaders(),
            body: json({
                invitation_token: token,
                accept,
                section,
            }),
        }),
    );
};

export { respondToInvitation };
