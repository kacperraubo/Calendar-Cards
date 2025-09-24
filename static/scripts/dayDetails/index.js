import { getInputValue } from '../utilities/inputs.js';
import '../common/sectionManagement.js';

const days = document.querySelectorAll('.day:not(.previous-month)');
const token = getInputValue('section-token');

days.forEach((day) => {
    day.addEventListener('click', () => {
        window.location.href = `/sections/${token}/days/${day.dataset.date}`;
    });
});
