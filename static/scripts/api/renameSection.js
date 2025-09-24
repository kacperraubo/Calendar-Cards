import { generateRequestHeaders } from './generateRequestHeaders.js';
import { json } from './utils.js';
import { wrapResponse } from './wrapResponse.js';

const renameSection = async ({ token, name }) => {
    const url = `/sections/${token}/rename`;

    return wrapResponse(
        fetch(url, {
            method: 'POST',
            headers: generateRequestHeaders(),
            body: json({
                name,
            }),
        }),
    );
};

export { renameSection };
