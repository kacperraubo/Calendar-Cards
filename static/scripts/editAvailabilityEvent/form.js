import { editAvailabilityEvent } from '../api/editAvailabilityEvent.js';
import { getInputValue } from '../utilities/inputs.js';
import { redirectWithExistingSearchParams } from '../utilities/urls.js';

const submitButton = document.querySelector('.save-event-button');
const token = getInputValue('event-token');
const remindersList = document.querySelector('.reminders-list');

submitButton.addEventListener('click', async () => {
    const reminders = Array.from(remindersList.children).map(
        (reminder) => reminder.dataset.value,
    );

    const { success, payload, errorMessage } = await editAvailabilityEvent({
        token,
        reminders,
    });

    if (success) {
        redirectWithExistingSearchParams(`/${payload.redirect}`);
    } else {
        alert(errorMessage || 'Something went wrong.');
    }
});
