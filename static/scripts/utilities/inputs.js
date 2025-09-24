const getInputValue = (name, cast = null) => {
    const value = document.querySelector(`[name="${name}"]`).value;

    return cast ? cast(value) : value;
};

export { getInputValue };
