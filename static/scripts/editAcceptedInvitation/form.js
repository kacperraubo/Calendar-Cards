import { editAcceptedInvitation } from '../api/editAcceptedInvitation.js';
import { getInputValue } from '../utilities/inputs.js';
import { redirectWithExistingSearchParams } from '../utilities/urls.js';

const sectionSelect = document.querySelector('select[name="section"]');
const submitButton = document.querySelector('.save-invitation-button');
const token = getInputValue('invitation-token');
const remindersList = document.querySelector('.reminders-list');

submitButton.addEventListener('click', async () => {
    if (!sectionSelect.value) {
        alert('Section is required');
        return;
    }

    const section = sectionSelect.value;
    const reminders = Array.from(remindersList.children).map(
        (reminder) => reminder.dataset.value,
    );

    const { success, payload, errorMessage } = await editAcceptedInvitation({
        token,
        section,
        reminders,
    });

    if (success) {
        redirectWithExistingSearchParams(`/${payload.redirect}`);
    } else {
        alert(errorMessage || 'Something went wrong.');
    }
});
