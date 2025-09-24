import { getInputValue } from '../utilities/inputs.js';
import { editEvent } from '../api/editEvent.js';
import { deleteEvent } from '../api/deleteEvent.js';
import { getSelectedDays } from '../common/daySelection.js';
import {
    getSearchParams,
    redirectWithSearchParams,
} from '../utilities/urls.js';

const token = getInputValue('event-token');
const section = getInputValue('section-token');
const titleInput = document.querySelector('input[name="title"]');
const descriptionInput = document.querySelector('textarea[name="description"]');
const addressInput = document.querySelector('input[name="address"]');
const guestList = document.querySelector('.guest-list.to-be-invited');
const remindersList = document.querySelector('.reminders-list');
const startTimeInput = document.querySelector('input[name="start-time"]');
const endTimeInput = document.querySelector('input[name="end-time"]');
const submitButton = document.querySelector('.save-event-button');
const allDayCheckbox = document.querySelector('input[name="all-day"]');
const sectionSelect = document.querySelector('select[name="section"]');

const eventDates = getInputValue('event-dates').split(',');

submitButton.addEventListener('click', async () => {
    const title = titleInput.value.trim();
    const description = descriptionInput.value.trim();
    const address = addressInput.value.trim();
    const guests = Array.from(guestList.children).map(
        (guest) => guest.textContent,
    );
    const reminders = Array.from(remindersList.children).map(
        (reminder) => reminder.dataset.value,
    );
    const selectedDates = getSelectedDays();
    const startTime = startTimeInput.value;
    const endTime = endTimeInput.value;

    if (!sectionSelect.value) {
        alert('Section is required');
        return;
    }

    if (!title) {
        alert('Title is required');
        return;
    }

    if (selectedDates.length === 0) {
        alert('At least one date must be selected');
        return;
    }

    if (!allDayCheckbox.checked && (!startTime || !endTime)) {
        alert(
            'You must either check "All day" or provide a start and end time',
        );
        return;
    }

    const daysOnPage = document.querySelectorAll('.day');

    let deletedDates = [];
    let addedDates = [];

    for (const date of selectedDates) {
        if (!eventDates.includes(date)) {
            addedDates.push(date);
        }
    }

    for (const day of daysOnPage) {
        if (
            !day.classList.contains('selected') &&
            eventDates.includes(day.dataset.date) &&
            !day.dataset.isPreviousMonth
        ) {
            deletedDates.push(day.dataset.date);
        }
    }

    const { success, payload, errorMessage } = await editEvent({
        token,
        title,
        description,
        guests,
        address,
        addedDates,
        deletedDates,
        reminders,
        section: sectionSelect.value,
        startTime: allDayCheckbox.checked ? null : startTime,
        endTime: allDayCheckbox.checked ? null : endTime,
    });

    if (success) {
        const relevantSearchParams = getSearchParams(
            'start-date',
            'display-mode',
        );

        redirectWithSearchParams(`/${payload.redirect}`, relevantSearchParams);
    } else {
        alert(errorMessage || 'An error occurred');
    }
});

const deleteButton = document.querySelector('.delete-event-button');

deleteButton.addEventListener('click', async () => {
    if (!confirm('Are you sure you want to delete this event?')) {
        return;
    }

    const { success, errorMessage } = await deleteEvent({ token });

    if (success) {
        const relevantQueryParams = getSearchParams(
            'start-date',
            'display-mode',
        );

        redirectWithSearchParams(`/${section}`, relevantQueryParams);
    } else {
        alert(errorMessage || 'An error occurred');
    }
});
