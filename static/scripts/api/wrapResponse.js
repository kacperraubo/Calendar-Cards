const wrapResponse = async (promise) => {
    const returnValue = {
        success: false,
        payload: null,
        error: null,
        errorMessage: null,
        response: null,
    };

    try {
        const response = await promise;
        returnValue.response = response;
        const json = await response.json();

        if (!json.success) {
            returnValue.error = json.error;
            returnValue.errorMessage = json.error.message;
        } else {
            returnValue.payload = json.payload;
            returnValue.success = true;
        }
    } catch (error) {
        returnValue.success = false;
        returnValue.error = error;
    }

    if (returnValue.error) {
        console.error(returnValue.error);
    }

    return returnValue;
};

export { wrapResponse };
