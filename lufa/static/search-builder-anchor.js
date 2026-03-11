/**
 * Applies SearchBuilder state from URL hash when the table initializes.
 *
 * @returns {void}
 */
function onAnchorTableInit(anchor_table) {
	let hash = location.hash.replace('#','');
	anchor_table.on("draw", () => onAnchorTableDraw(anchor_table));

	if (hash === ""){
		return;
	}

	let j = decodeURIComponent(hash);
	let d = JSON.parse(j);

	anchor_table.searchBuilder.rebuild(d);
}

/**
 * Persists current SearchBuilder state into the URL hash after redraw.
 *
 * @returns {void}
 */
function onAnchorTableDraw(anchor_table) {
	let d = anchor_table.searchBuilder.getDetails();
	let j = JSON.stringify(d)

	if (j === "{}"){
		location.hash = '';
	} else {
		location.hash = encodeURIComponent(j);
	}
}
