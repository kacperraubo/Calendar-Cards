const days = document.querySelectorAll('.day');

days.forEach((day) => {
    day.addEventListener('click', () => {
        if (day.dataset.isPreviousMonth) {
            return;
        }

        day.classList.toggle('selected');
    });
});

const getSelectedDays = () => {
    return Array.from(document.querySelectorAll('.day.selected')).map(
        (day) => day.dataset.date,
    );
};

export { getSelectedDays };
