import { addSection } from '../api/addSection.js';
import { isAnonymous } from '../utilities/userStatus.js';

const addSectionButton = document.querySelector('.add-section-button');

addSectionButton.addEventListener('click', async () => {
    if (isAnonymous) {
        alert('You must be logged in to add a section');
        return;
    }

    const name = prompt('Enter the name of the section');

    if (!name) {
        return;
    }

    const { success, payload, errorMessage } = await addSection({ name });

    if (success) {
        alert('Section added');
        window.location.href = `/${payload.token}`;
    } else {
        alert(errorMessage || 'Something went wrong');
    }
});
