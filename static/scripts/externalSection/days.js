import {
    getSearchParams,
    redirectWithSearchParams,
} from '../utilities/urls.js';
import { getInputValue } from '../utilities/inputs.js';

const section = getInputValue('section-token');
const days = document.querySelectorAll('.day');
const dayOptionsContainer = document.querySelector('.day-options');
const dayOptionsMobileMenuContainer =
    dayOptionsContainer.querySelector('.mobile-menu');
const dayOptionsOpenButton = dayOptionsContainer.querySelector('.icon');
const addEventButtons = document.querySelectorAll('.add-event-button');
const timeSelect = document.querySelector('.time-select');

let selectedDay = null;

days.forEach((day) => {
    day.addEventListener('click', () => {
        if (day.dataset.isPreviousMonth) {
            return;
        }

        if (selectedDay === day) {
            dayOptionsContainer.classList.add('hidden');
            day.classList.remove('selected');
            selectedDay = null;
            dayOptionsMobileMenuContainer.classList.add('hidden');
            return;
        }

        if (selectedDay) {
            selectedDay.classList.remove('selected');
        }

        if (!day.dataset.hasAvailability) {
            addEventButtons.forEach((button) => {
                button.classList.add('disabled');
                button.title = 'The owner is not available on this day';
            });
        } else {
            addEventButtons.forEach((button) => {
                button.classList.remove('disabled');
                button.title = '';
            });
        }

        day.classList.add('selected');
        selectedDay = day;

        dayOptionsContainer.classList.remove('hidden');
    });
});

dayOptionsOpenButton.addEventListener('click', () => {
    dayOptionsMobileMenuContainer.classList.toggle('hidden');

    if (dayOptionsMobileMenuContainer.classList.contains('hidden')) {
        timeSelect.classList.add('hidden');
    }
});

addEventButtons.forEach((button) => {
    button.addEventListener('click', () => {
        if (button.classList.contains('disabled')) {
            return;
        }

        const relevantSearchParams = getSearchParams(
            'start-date',
            'display-mode',
        );
        const selectedDay = document.querySelector('.day.selected');

        redirectWithSearchParams(
            `/external/availability/${selectedDay.dataset.availabilityToken}`,
            relevantSearchParams,
        );
    });
});
