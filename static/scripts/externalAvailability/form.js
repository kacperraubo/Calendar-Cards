import { getInputValue } from '../utilities/inputs.js';
import { createEventForAvailability } from '../api/createEventForAvailability.js';

const token = getInputValue('availability-token');
const titleInput = document.querySelector('input[name="title"]');
const descriptionInput = document.querySelector('textarea[name="description"]');
const addressInput = document.querySelector('input[name="address"]');
const startTimeInput = document.querySelector('input[name="start-time"]');
const endTimeInput = document.querySelector('input[name="end-time"]');
const submitButton = document.querySelector('.create-event-button');
const emailInput = document.querySelector('input[name="email"]');

submitButton.addEventListener('click', async () => {
    const title = titleInput.value.trim();
    const description = descriptionInput.value.trim();
    const address = addressInput.value.trim();
    const startTime = startTimeInput.value;
    const endTime = endTimeInput.value;

    if (emailInput && !emailInput.value) {
        alert('Email is required');
        return;
    }

    if (!title) {
        alert('Title is required');
        return;
    }

    const { success, payload, errorMessage } = await createEventForAvailability(
        {
            token,
            title,
            description,
            address,
            startTime,
            endTime,
            email: emailInput ? emailInput.value : null,
        },
    );

    if (success) {
        alert('Event created');
        window.location.href = `/external/section/${payload.redirect}`;
    } else {
        alert(errorMessage || 'An error occurred');
    }
});
