/**
 * Applies a Bootstrap row color class based on callback state.
 *
 * @param {HTMLElement} row Table row element.
 * @param {string} state Ansible callback state.
 * @returns {void}
 */
function colorizeTableCell(row, state) {
	if (state === 'unreachable' || state === 'failed') {
		$(row).addClass('table-danger');
	} else if (state === 'changed') {
		$(row).addClass('table-warning');
	} else if (state === 'ok') {
		$(row).addClass('table-success');
	} else if (state === 'skipped') {
		$(row).addClass('table-info');
	} else if (state === 'rescued') {
		$(row).addClass('table-primary');
	} else if (state === 'ignored') {
		$(row).addClass('table-secondary');
	}
}
