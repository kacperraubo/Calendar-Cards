import { deleteSection } from '../api/deleteSection.js';
import { getInputValue } from '../utilities/inputs.js';
import { isAnonymous } from '../utilities/userStatus.js';

const deleteSectionButton = document.querySelector('.delete-section-button');
const section = getInputValue('section-token');

deleteSectionButton.addEventListener('click', async () => {
    if (isAnonymous) {
        alert('You must be logged in to delete a section');
        return;
    }

    if (!confirm('Are you sure you want to delete this section?')) {
        return;
    }

    const { success, payload, errorMessage } = await deleteSection({
        token: section,
    });

    if (success) {
        alert('Section deleted');
        window.location.href = `/${payload.redirect}`;
    } else {
        alert(errorMessage || 'Something went wrong');
    }
});
