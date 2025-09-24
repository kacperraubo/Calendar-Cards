const localTimeZoneName = Intl.DateTimeFormat().resolvedOptions().timeZone;

const getFormattedTimeZone = () => {
    const date = new Date();

    const offset = date.getTimezoneOffset();
    const sign = offset >= 0 ? '+' : '-';
    const hours = Math.floor(Math.abs(offset) / 60)
        .toString()
        .padStart(2, '0');
    const minutes = (Math.abs(offset) % 60).toString().padStart(2, '0');

    const gmtOffset = `(GMT${sign}${hours}:${minutes})`;

    const formatter = new Intl.DateTimeFormat('en-US', {
        timeZone: localTimeZoneName,
        timeZoneName: 'long',
    });
    const parts = formatter.formatToParts(date);
    const timeZoneName = parts.find(
        (part) => part.type === 'timeZoneName',
    ).value;

    return `${gmtOffset} ${timeZoneName} - ${localTimeZoneName
        .split('/')[1]
        .replace('_', ' ')}`;
};

/**
 * @param {Date} date
 * @returns
 */
const dateParts = (date) => {
    return {
        fullYear: date.getFullYear(),
        month: date.getMonth(),
        monthName: date.toLocaleString('en-US', { month: 'long' }),
        day: date.getDate(),
        weekday: date.toLocaleString('en-US', { weekday: 'long' }),
        hours: date.getHours(),
        minutes: date.getMinutes(),
        seconds: date.getSeconds(),
        milliseconds: date.getMilliseconds(),
    };
};

export { localTimeZoneName as localTimeZone, getFormattedTimeZone, dateParts };
