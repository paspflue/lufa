#!/bin/bash
set -e  # Exit on error

SCRIPT_DIR="$(dirname "$0")"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
PROJECT_DEST="lufa/static/dist"
DIST_DIR="$PROJECT_ROOT/$PROJECT_DEST"
NODE_MODULES="$PROJECT_ROOT/node_modules"

copy_into(){
  mkdir -p "$2" && cp "$1" "$2"
}

echo "Copy frontend dependencies to $PROJECT_DEST"

# Bootstrap
copy_into "$NODE_MODULES/bootstrap/dist/css/bootstrap.min.css" "$DIST_DIR/bootstrap/"
copy_into "$NODE_MODULES/bootstrap/dist/css/bootstrap.min.css.map" "$DIST_DIR/bootstrap/"
copy_into "$NODE_MODULES/bootstrap/dist/js/bootstrap.bundle.min.js" "$DIST_DIR/bootstrap/"
copy_into "$NODE_MODULES/bootstrap/dist/js/bootstrap.bundle.min.js.map" "$DIST_DIR/bootstrap/"

# jQuery
copy_into "$NODE_MODULES/jquery/dist/jquery.min.js" "$DIST_DIR/jquery/"
copy_into "$NODE_MODULES/jquery/dist/jquery.min.map" "$DIST_DIR/jquery/"

# DataTables
copy_into "$NODE_MODULES/datatables.net/js/dataTables.min.js" "$DIST_DIR/datatables/"
copy_into "$NODE_MODULES/datatables.net-bs5/css/dataTables.bootstrap5.min.css" "$DIST_DIR/datatables/"
copy_into "$NODE_MODULES/datatables.net-bs5/js/dataTables.bootstrap5.min.js" "$DIST_DIR/datatables/"

# DataTables Datetime
copy_into "$NODE_MODULES/datatables.net-datetime/dist/dataTables.dateTime.js" "$DIST_DIR/datatables-datetime/"
copy_into "$NODE_MODULES/datatables.net-datetime/dist/dataTables.dateTime.css" "$DIST_DIR/datatables-datetime/"

# DataTables Buttons
copy_into "$NODE_MODULES/datatables.net-buttons/js/dataTables.buttons.min.js" "$DIST_DIR/datatables/"
copy_into "$NODE_MODULES/datatables.net-buttons/js/buttons.html5.min.js" "$DIST_DIR/datatables/"
copy_into "$NODE_MODULES/datatables.net-buttons/js/buttons.colVis.min.js" "$DIST_DIR/datatables/"
copy_into "$NODE_MODULES/datatables.net-buttons-bs5/js/buttons.bootstrap5.min.js" "$DIST_DIR/datatables/"
copy_into "$NODE_MODULES/datatables.net-buttons-bs5/css/buttons.bootstrap5.min.css" "$DIST_DIR/datatables/"

# DataTables SearchBuilder
copy_into "$NODE_MODULES/datatables.net-searchbuilder/js/dataTables.searchBuilder.min.js" "$DIST_DIR/datatables/"
copy_into "$NODE_MODULES/datatables.net-searchbuilder-bs5/js/searchBuilder.bootstrap5.min.js" "$DIST_DIR/datatables/"
copy_into "$NODE_MODULES/datatables.net-searchbuilder-bs5/css/searchBuilder.bootstrap5.min.css" "$DIST_DIR/datatables/"

# JSZip (required for Excel export)
copy_into "$NODE_MODULES/jszip/dist/jszip.min.js" "$DIST_DIR/jszip/"

# Luxon
copy_into "$NODE_MODULES/luxon/build/global/luxon.min.js" "$DIST_DIR/luxon/"

# Font Awesome (CSS + Webfonts with original structure)
copy_into "$NODE_MODULES/@fortawesome/fontawesome-free/css/all.min.css" "$DIST_DIR/fontawesome/css/"
cp -r "$NODE_MODULES/@fortawesome/fontawesome-free/webfonts" "$DIST_DIR/fontawesome/"

echo ""
echo "All assets copied to $PROJECT_DEST"
