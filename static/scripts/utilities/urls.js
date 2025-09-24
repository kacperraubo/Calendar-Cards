/**
 * @param {string} url
 */
const redirectWithExistingSearchParams = (url) => {
    const currentQueryParams = window.location.search;

    if (currentQueryParams) {
        window.location.href = `${url}${currentQueryParams}`;
    } else {
        window.location.href = url;
    }
};

/**
 * @param  {...str} keys
 */
const getSearchParams = (...keys) => {
    const existingSearchParams = new URLSearchParams(window.location.search);
    const searchParams = new URLSearchParams();

    keys.forEach((key) => {
        if (existingSearchParams.has(key)) {
            searchParams.append(key, existingSearchParams.get(key));
        }
    });

    return searchParams;
};

/**
 * @param {string} url
 * @param {URLSearchParams} params
 */
const redirectWithSearchParams = (url, params) => {
    window.location.href = `${url}?${params.toString()}`;
};

export {
    redirectWithExistingSearchParams,
    getSearchParams,
    redirectWithSearchParams,
};
