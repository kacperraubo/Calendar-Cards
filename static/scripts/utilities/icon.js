const cache = new Map();

/**
 * @param {string} iconName
 * @param {string} className
 * @param {object | undefined} extra
 * @returns
 */
const getIcon = async (iconName, className, extra) => {
    const temporaryElement = document.createElement('div');

    let svgText;

    if (cache.has(iconName)) {
        svgText = cache.get(iconName);
    } else {
        const response = await fetch(`/static/images/icons/${iconName}.svg`);
        svgText = await response.text();

        cache.set(iconName, svgText);
    }

    temporaryElement.innerHTML = svgText;

    const icon = temporaryElement.querySelector('svg');
    icon.classList = className;

    if (extra) {
        for (const [key, value] of Object.entries(extra)) {
            icon.setAttribute(key, value);
        }
    }

    return icon;
};

export { getIcon };
