/**
 * Restores SearchBuilder filters from the URL hash.
 *
 * @param {DataTable} anchor_table DataTable instance.
 * @returns {boolean|void} True when a filter was applied.
 */
function setFilterFromSharedURL(anchor_table) {
    // take the hash part of the shared URL
    // the hash part contains the filter criteria that were shared
    let hash = location.hash.replace('#', '');

    if (hash === '') {
        // this means a normal URL was opened
        // not a shared filter URL
        return;
    }

    let j = decodeURIComponent(hash);
    let d = JSON.parse(j);
    anchor_table.searchBuilder.rebuild(d);
    return true
};

/**
 * Converts SearchBuilder details to a shareable URL hash.
 *
 * @param {object} searchBuilderDetails SearchBuilder details object.
 * @returns {string} Encoded hash string or empty string.
 */
function getURLHashFromSearchBuilder(searchBuilderDetails) {
    let j = JSON.stringify(searchBuilderDetails);
    if (j === '{}') {
        return '';
    }
    return '#' + encodeURIComponent(j);
}

/**
 * Creates the DataTables button config for sharing current filters.
 *
 * @returns {object} DataTables button configuration.
 */
function filterSharingButton() {
    return {
        text: 'Share',
        action: (e, dt, node, config) => {
            // save the current filter state as a parameter in a URL
            let hashValue;
            try {
                hashValue = getURLHashFromSearchBuilder(dt.searchBuilder.getDetails());
            } catch (error) {
                globalThis.alert('Error: ' + error);
                return;
            }
            let full_url = globalThis.location.origin + globalThis.location.pathname + hashValue;

            navigator.clipboard.writeText(full_url);
        }
    };
}
