let cachedToken = null;

const getCsrfToken = () => {
    if (cachedToken) {
        return cachedToken;
    }

    cachedToken = document.querySelector('[name="csrfmiddlewaretoken"]').value;

    return cachedToken;
};

export { getCsrfToken };
