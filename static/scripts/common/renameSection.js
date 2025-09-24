import { renameSection } from '../api/renameSection.js';

const renameSectionButton = document.querySelector('.rename-section-button');
const selectedSections = document.querySelectorAll('.section.selected');

if (renameSectionButton && selectedSections.length > 0) {
    const token = selectedSections[0].dataset.token;

    renameSectionButton.addEventListener('click', async () => {
        const name = prompt('Enter the new name of the section');

        if (!name) {
            return;
        }

        const { success, errorMessage } = await renameSection({
            token,
            name,
        });

        if (success) {
            alert('Section renamed');

            for (const section of selectedSections) {
                section.textContent = name;
            }
        } else {
            alert(errorMessage || 'Something went wrong');
        }
    });
}
