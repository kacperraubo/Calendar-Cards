import { generateRequestHeaders } from './generateRequestHeaders.js';
import { json } from './utils.js';
import { wrapResponse } from './wrapResponse.js';

const addSection = async ({ name }) => {
    const url = `/sections/add`;

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

export { addSection };
