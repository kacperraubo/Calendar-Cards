class Files {
    constructor(files) {
        this.files = Array.from(files);
    }
}

const formData = ({ ...data }) => {
    const formData = new FormData();

    for (const [key, value] of Object.entries(data)) {
        if (value instanceof Files) {
            for (const file of value.files) {
                formData.append(key, file);
            }

            continue;
        }

        formData.append(key, value);
    }

    return formData;
};

const json = (data) => {
    return JSON.stringify(data);
};

export { Files, formData, json };
