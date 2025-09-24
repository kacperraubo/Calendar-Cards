import { generateRequestHeaders } from './generateRequestHeaders.js';
import { wrapResponse } from './wrapResponse.js';

const deleteSection = async ({ token }) => {
    const url = `/sections/${token}/delete`;

    return wrapResponse(
        fetch(url, {
            method: 'POST',
            headers: generateRequestHeaders(),
        }),
    );
};

export { deleteSection };
