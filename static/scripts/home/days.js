import {
    getSearchParams,
    redirectWithSearchParams,
} from '../utilities/urls.js';
import { getInputValue } from '../utilities/inputs.js';
import { isAnonymous } from '../utilities/userStatus.js';

const section = getInputValue('section-token');
const days = document.querySelectorAll('.day');
const upcomingEventContainer = document.querySelector('.upcoming-event');
const dayOptionsContainer = document.querySelector('.day-options');
const dayOptionsMobileMenuContainer =
    dayOptionsContainer.querySelector('.mobile-menu');
const dayOptionsOpenButton = dayOptionsContainer.querySelector('.icon');
const addEventButtons = document.querySelectorAll('.add-event-button');
const viewButtons = document.querySelectorAll('.view-button');
const viewDivider = document.querySelector('.view-divider');
const intervals = document.querySelector('.intervals');

let selection = [];

const hide = (elements) => {
    elements.forEach((element) => element.classList.add('hidden'));
};

const show = (elements) => {
    elements.forEach((element) => element.classList.remove('hidden'));
};

days.forEach((day) => {
    day.addEventListener('click', () => {
        if (day.dataset.isPreviousMonth) {
            return;
        }

        if (selection.includes(day)) {
            selection = selection.filter((selectedDay) => selectedDay !== day);
            day.classList.remove('selected');
        } else {
            selection.push(day);
            day.classList.add('selected');
        }

        if (selection.length === 0) {
            dayOptionsContainer.classList.add('hidden');
            upcomingEventContainer.classList.remove('hidden');
            dayOptionsMobileMenuContainer.classList.add('hidden');
        } else if (selection.length > 1) {
            intervals.classList.add('hidden');
            dayOptionsContainer.classList.remove('hidden');
            upcomingEventContainer.classList.add('hidden');
        } else {
            dayOptionsContainer.classList.remove('hidden');
            upcomingEventContainer.classList.add('hidden');
        }

        if (selection.length === 1) {
            show(viewButtons);
            viewDivider.classList.remove('hidden');
        } else {
            hide(viewButtons);
            viewDivider.classList.add('hidden');
        }
    });
});

viewButtons.forEach((button) => {
    button.addEventListener('click', () => {
        if (isAnonymous) {
            alert('You must be logged in to view day details');
            return;
        }

        window.location.href = `/sections/${section}/days/${selection[0].dataset.date}`;
    });
});

dayOptionsOpenButton.addEventListener('click', () => {
    dayOptionsMobileMenuContainer.classList.toggle('hidden');

    if (dayOptionsMobileMenuContainer.classList.contains('hidden')) {
        intervals.classList.add('hidden');
    }
});

addEventButtons.forEach((button) => {
    button.addEventListener('click', () => {
        if (isAnonymous) {
            alert('You must be logged in to add an event');
            return;
        }

        const relevantSearchParams = getSearchParams(
            'start-date',
            'display-mode',
        );

        for (const selectedDay of selection) {
            relevantSearchParams.append(
                'selected-days[]',
                selectedDay.dataset.date,
            );
        }
        relevantSearchParams.append('section', section);

        redirectWithSearchParams('/events/create', relevantSearchParams);
    });
});
