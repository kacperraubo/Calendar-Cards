import { getInputValue } from '../utilities/inputs.js';
import { createEvent } from '../api/createEvent.js';
import { getSelectedDays } from '../common/daySelection.js';
import {
    getSearchParams,
    redirectWithSearchParams,
} from '../utilities/urls.js';

const section = getInputValue('section-token');
const titleInput = document.querySelector('input[name="title"]');
const descriptionInput = document.querySelector('textarea[name="description"]');
const addressInput = document.querySelector('input[name="address"]');
const guestList = document.querySelector('.guest-list');
const remindersList = document.querySelector('.reminders-list');
const startTimeInput = document.querySelector('input[name="start-time"]');
const endTimeInput = document.querySelector('input[name="end-time"]');
const submitButton = document.querySelector('.create-event-button');
const allDayCheckbox = document.querySelector('input[name="all-day"]');

submitButton.addEventListener('click', async () => {
    const title = titleInput.value.trim();
    const description = descriptionInput.value.trim();
    const address = addressInput.value.trim();
    const guests = Array.from(guestList.children).map(
        (guest) => guest.textContent,
    );
    const dates = getSelectedDays();
    const startTime = startTimeInput.value;
    const endTime = endTimeInput.value;
    const reminders = Array.from(remindersList.children).map(
        (reminder) => reminder.dataset.value,
    );

    if (!title) {
        alert('Title is required');
        return;
    }

    if (dates.length === 0) {
        alert('At least one date must be selected');
        return;
    }

    if (!allDayCheckbox.checked && (!startTime || !endTime)) {
        alert(
            'You must either check "All day" or provide a start and end time',
        );
        return;
    }

    const { success, errorMessage } = await createEvent({
        section,
        title,
        description,
        guests,
        address,
        dates,
        startTime,
        endTime,
        reminders,
    });

    if (success) {
        const existingSection = getSearchParams('section').get('section');
        const relevantQueryParams = getSearchParams(
            'start-date',
            'display-mode',
        );

        redirectWithSearchParams(`/${existingSection}`, relevantQueryParams);
    } else {
        alert(errorMessage || 'An error occurred');
    }
});
