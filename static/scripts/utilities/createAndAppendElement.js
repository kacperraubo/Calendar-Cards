function createAndAppendElement(tagName, parentElement, classes, attributes) {
    // Create a new HTML element
    const newElement = document.createElement(tagName);

    // Add specified classes to the new element
    if (classes && Array.isArray(classes)) {
        newElement.classList.add(...classes);
    }

    // Add specified attributes to the new element
    if (attributes && typeof attributes === 'object') {
        for (const attribute in attributes) {
            if (attributes.hasOwnProperty(attribute)) {
                newElement.setAttribute(attribute, attributes[attribute]);
            }
        }
    }

    // Append the new element to the specified parent element in the DOM
    parentElement.appendChild(newElement);

    return newElement;
}
