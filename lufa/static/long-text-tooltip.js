/**
 * Shortens long table cell text and keeps full content in a tooltip.
 *
 * @param {string|null} data Cell value.
 * @param {string} type DataTables render type.
 * @returns {string|null} Rendered text or original value.
 */
function useLongTextTooltip(data, type) {
    const LIMIT_MAX_CHARS = 50;
    if (data !== null) {
        if (type === 'display' && data.length > LIMIT_MAX_CHARS) {
            const shortText = data.substring(0, LIMIT_MAX_CHARS) + '...';
            return `<span title="${data}">${shortText}</span>`;
        }
    }
    return data;
}
