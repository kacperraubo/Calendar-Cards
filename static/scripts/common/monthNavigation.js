const currentQueryParams = new URLSearchParams(window.location.search);
const displayMode = currentQueryParams.get('display-mode');
const startDate = currentQueryParams.get('start-date');

let date;

if (startDate) {
    const [year, month] = startDate.split('-').map((val) => parseInt(val, 10));
    date = new Date(year, month - 1, 1);
} else {
    date = new Date();
}

const nextButtons = document.querySelectorAll('.next-month-button');
const previousButtons = document.querySelectorAll('.previous-month-button');

nextButtons.forEach((button) => {
    button.addEventListener('click', () => {
        const newDate = new Date(new Date(date).setMonth(date.getMonth() + 1));
        const urlParams = new URLSearchParams();

        for (const [key, value] of currentQueryParams) {
            urlParams.set(key, value);
        }

        urlParams.set(
            'start-date',
            `${newDate.getFullYear()}-${newDate.getMonth() + 1}`,
        );

        if (displayMode) {
            urlParams.set('display-mode', displayMode);
        }

        const url = `${window.location.origin}${
            window.location.pathname
        }?${urlParams.toString()}`;
        window.location.href = url;
    });
});

previousButtons.forEach((button) => {
    button.addEventListener('click', () => {
        const newDate = new Date(new Date(date).setMonth(date.getMonth() - 1));
        const urlParams = new URLSearchParams();

        for (const [key, value] of currentQueryParams) {
            urlParams.set(key, value);
        }

        urlParams.set(
            'start-date',
            `${newDate.getFullYear()}-${newDate.getMonth() + 1}`,
        );

        if (displayMode) {
            urlParams.set('display-mode', displayMode);
        }

        const url = `${window.location.origin}${
            window.location.pathname
        }?${urlParams.toString()}`;
        window.location.href = url;
    });
});

const singleModeButton = document.querySelector('.display-modes .single');
const multiModeButton = document.querySelector('.display-modes .multi');
const yearModeButton = document.querySelector('.display-modes .year');

singleModeButton.addEventListener('click', () => {
    const urlParams = new URLSearchParams();

    for (const [key, value] of currentQueryParams) {
        urlParams.set(key, value);
    }

    urlParams.set('display-mode', 'single');

    if (startDate) {
        urlParams.set('start-date', startDate);
    }

    const url = `${window.location.origin}${
        window.location.pathname
    }?${urlParams.toString()}`;
    window.location.href = url;
});

multiModeButton.addEventListener('click', () => {
    const urlParams = new URLSearchParams();

    for (const [key, value] of currentQueryParams) {
        urlParams.set(key, value);
    }

    urlParams.set('display-mode', 'multi');

    if (startDate) {
        urlParams.set('start-date', startDate);
    }

    const url = `${window.location.origin}${
        window.location.pathname
    }?${urlParams.toString()}`;
    window.location.href = url;
});

yearModeButton.addEventListener('click', () => {
    const urlParams = new URLSearchParams();

    for (const [key, value] of currentQueryParams) {
        urlParams.set(key, value);
    }

    urlParams.set('display-mode', 'year');

    if (startDate) {
        urlParams.set('start-date', startDate);
    }

    const url = `${window.location.origin}${
        window.location.pathname
    }?${urlParams.toString()}`;
    window.location.href = url;
});
