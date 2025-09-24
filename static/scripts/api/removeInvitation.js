import { generateRequestHeaders } from './generateRequestHeaders.js';
import { wrapResponse } from './wrapResponse.js';

const removeInvitation = async ({ token }) => {
    const url = `/invitations/${token}/remove`;

    return wrapResponse(
        fetch(url, {
            method: 'POST',
            headers: generateRequestHeaders(),
        }),
    );
};

export { removeInvitation };
