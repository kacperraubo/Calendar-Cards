import { generateRequestHeaders } from './generateRequestHeaders.js';
import { wrapResponse } from './wrapResponse.js';

const leaveInvitation = async ({ token }) => {
    const url = `/invitations/${token}/leave`;

    return wrapResponse(
        fetch(url, {
            method: 'POST',
            headers: generateRequestHeaders(),
        }),
    );
};

export { leaveInvitation };
