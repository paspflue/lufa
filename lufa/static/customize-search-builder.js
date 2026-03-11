/**
 * Applies specific search criteria to a DataTable instance by rebuilding its search builder state.
 * The method constructs a search criteria object and updates the table's search builder accordingly.
 *
 * @param {string} table_id The selector or ID of the DataTable element to which the search builder will be applied.
 * @param {HTMLElement} element The DOM element containing the text content used to determine whether the search should proceed.
 * @param {*} data The primary data field to be used in the search criteria.
 * @param {*} origData The original data field to be used in the search criteria.
 * @param {*} value The value to match against in the search condition.
 * @return {void} This method does not return a value.
 */
function applySearchBuilder(table_id, element, data, origData, value){
    const table = $(table_id).DataTable()
    if(element.textContent > 0 || element.textContent.length > 1) {
        // element.textContent > 0 refers to the number of the respective status category
        // element.textContent.length > 1 refers to the length of the text
        const search_state = {
            criteria: [
                {
                    data: data, 
                    origData: origData,
                    condition: '=',
                    value: [value]
                }
            ],
            logic: 'AND'
        };
        console.log(search_state);
        table.searchBuilder.rebuild(search_state, true)
    };

};

/**
 * Extends the search builder filter with the provided input and saves it for subsequent operations.
 *
 * @param {string} table_id The ID of the DataTable to which the search builder is applied.
 * @param {HTMLElement} element The HTML element containing the text/content to evaluate.
 * @param {string} data The name or label of the column being filtered.
 * @param {string} origData The original data key for the column.
 * @param {string|number} value The value to be used in the filter's condition.
 * @param {string} type The data type of the value being filtered (e.g., string, number).
 * @return {void} This function does not return a value; it updates the current filter state and stores it in localStorage.
 */
function extendSearchBuilder(table_id, element, data, origData, value, type) {
    const table = $(table_id).DataTable()
    if(element.textContent > 0 || element.textContent.length > 1) {

        const currentFilter = table.searchBuilder.getDetails();
        const newCondition = {
            condition: '=',
            data: data,
            origData: origData,
            type: type,
            value: [value]
        };

        if (!currentFilter.criteria) {
            currentFilter.criteria = [];
            currentFilter.logic = 'AND';
        }

        // the condition is only added if not already present
        const exists = currentFilter.criteria.some((cond) => {
            return cond.condition === newCondition.condition &&
                cond.data === newCondition.data &&
                cond.origData === newCondition.origData &&
                cond.type === newCondition.type &&
                JSON.stringify(cond.value) === JSON.stringify(newCondition.value);
        });
        if (!exists) {
            currentFilter.criteria.push(newCondition);
        };

        localStorage.setItem(
                'currentSearchBuilder', 
                JSON.stringify(currentFilter));
    };

};
