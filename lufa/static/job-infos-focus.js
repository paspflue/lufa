/**
 * Removes internal AWX and Tower keys from the given object.
 *
 * @param {object} data Source object.
 * @returns {object} Filtered object.
 */
function filterData(data) {

    const filtered = {};
    for (const key in data) {
        if (!key.startsWith('awx_') && !key.startsWith('tower_')) {
            filtered[key] = data[key];
        }
    }
    return filtered;
}

/**
 * Updates tooltip text for the extra vars switch.
 *
 * @param {HTMLElement} tooltipTrigger Switch element used as tooltip trigger.
 * @returns {boolean}
 */
function switchExtraVarsToolTip(tooltipTrigger){
  
  const tooltip = new bootstrap.Tooltip(tooltipTrigger, { trigger: 'hover'});
  tooltipTrigger.addEventListener('change', function () {
    const newTitle = this.checked ? 'Hide AWX variables' : 'Show AWX variables';
    tooltip.setContent({ '.tooltip-inner': newTitle });
  });
  return true

}

/**
 * Toggles rendering of filtered or full extra vars JSON.
 *
 * @param {string} originalData JSON string with extra vars.
 * @param {HTMLElement} preElement Target <pre> element.
 * @param {HTMLInputElement} extraVarsSwitch Toggle switch element.
 * @returns {boolean}
 */
function switchExtraVars(originalData, preElement, extraVarsSwitch){

    originalData = JSON.parse(originalData);
    // Default: AWX variables are hidden, switch inactive
    const filtered = filterData(originalData);
    preElement.textContent = JSON.stringify(filtered, null, 2);
    extraVarsSwitch.checked = false; 

    // Event listener for toggling
    extraVarsSwitch.addEventListener('change', function () {
		extraVarsSwitch.ariaChecked = String(Boolean(this.checked));
        if (this.checked) {
            // Switch active: show all data including AWX variables
            preElement.textContent = JSON.stringify(originalData, null, 2);
        } else {
            const filtered = filterData(originalData);
            preElement.textContent = JSON.stringify(filtered, null, 2);
        }
    });
    return true

}
