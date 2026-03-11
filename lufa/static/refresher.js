 /**
  * NullObject used internally in Refresher. 
  */
 class NullRefresher {
	onRefreshOnce() {}

	onRefreshRepeated() { }
 }

 /**
  * Used internally in Refresher. Adaptor for a given single function used to do the refresh.
  */
 class SimpleRefresher {
	/**
	 * Creates a refresher adapter for a single update function.
	 *
	 * @param {Function} updaterFunc Function called for one refresh.
	 */
	constructor(updaterFunc) {
		this.onRefreshOnce = updaterFunc;
	}

	/**
	 * Runs repeated refresh scheduling for function-based refreshers.
	 *
	 * @param {Refresher} refresher Refresher controller instance.
	 * @returns {void}
	 */
	onRefreshRepeated(refresher) {
		if (refresher.isRepeatedActive()) {
			this.onRefreshOnce(refresher);
		}
		/*
		This loop will always run. If the live switch is checked, it will
		reload the data of the site.

		It is recursively calling itself with delay. This prevents the loop
		from starting over, before the data is refreshed.
		see: https://developer.mozilla.org/en-US/docs/Web/API/setInterval

		If ajax.reload of a data table is finished, the xhr event starts
		the loop over.
		*/
		setTimeout(() => {
			this.onRefreshRepeated(refresher);
		}, refresher.intervallInMilliSec);
	}
 }

 /**
  * Used internally in Refresher. Adaptor for DataTables
  */
 class DataTablesXhrRefresher {
	/**
	 * Creates a refresher adapter for a DataTable instance.
	 *
	 * @param {DataTable} dataTable DataTable instance.
	 */
	constructor(dataTable) {
		this.dataTable = dataTable;
	}

	/**
	 * Triggers one ajax reload on the configured DataTable.
	 *
	 * @returns {void}
	 */
	onRefreshOnce() {
		this.dataTable.ajax.reload(null, false);
	}

	/**
	 * Registers repeated refresh scheduling via DataTables xhr events.
	 *
	 * @param {Refresher} refresher Refresher controller instance.
	 * @returns {void}
	 */
	onRefreshRepeated(refresher) {
		/**
		 * Internal loop that keeps scheduling the next reload.
		 *
		 * @returns {void}
		 */
		const reload_loop = () => {
			/*
			This loop will always run. If the live switch is checked, it will
			reload the data of the site.

			It is recursively calling itself with delay. This prevents the loop
			from starting over, before the data is refreshed.
			see: https://developer.mozilla.org/en-US/docs/Web/API/setInterval

			If ajax.reload of a data table is finished, the xhr event starts
			the loop over.
			*/
			const now = Date.now()

			if (this.lastRefreshRepeatedStarted === undefined || now - this.lastRefreshRepeatedStarted >= refresher.intervallInMilliSec) {
				this.lastRefreshRepeatedStarted = now;
				setTimeout(() => {
					if (refresher.isRepeatedActive()) {
						this.onRefreshOnce(refresher);
					} else {
						reload_loop();
					}
				}, refresher.intervallInMilliSec);
			}
		};
		this.dataTable.on('xhr', reload_loop);
	}
 }

	/***
	  * Refreshes the page on an intervall or manually.
	  */
		class Refresher {
		/**
		 * Creates the refresher controller and caches required DOM elements.
		 *
		 * @param {number} intervallInMilliSec Refresh interval in milliseconds.
		 */
		constructor(intervallInMilliSec) {
			this.intervallInMilliSec = intervallInMilliSec;
			this._implementation = new NullRefresher();
			this._enabled = false;
			this._localStorage = globalThis.localStorage;
			this._refresh_button = document.getElementById('refresh_button');
			this._live_switch = document.getElementById('live_switch');

			this._refresh_button.onclick = () => this.onRefreshOnce();
		}

		/**
		 * Setup watching page elements for changes.
		 * 
		 * @returns {Refresher}
		 */
		setupEventListeners() {
			this._live_switch.addEventListener('change', () => { globalThis.localStorage.setItem('live_switch', live_switch.checked ? 1 : 0); this._live_switch.ariaChecked = String(Boolean(live_switch.checked));});
			const stored = this._localStorage.getItem('live_switch');
			globalThis.addEventListener('storage', (event) => {if (event.key === 'live_switch') { this._live_switch.checked = event.newValue === '1'}});
			if (stored !== null) {
				this._live_switch.checked = stored === '1';
				this._live_switch.ariaChecked = String(Boolean(this._live_switch.checked));
			}
			return this;
		}

		/**
		 * Sets the concrete refresher implementation and starts repeated mode.
		 *
		 * @param {NullRefresher|SimpleRefresher|DataTablesXhrRefresher} implementation Active refresher adapter.
		 * @returns {void}
		 */
		_enableUpdater(implementation) {
			this._implementation = implementation;
			this.setEnabled(true);
			this._implementation.onRefreshRepeated(this);
		}

		/**
		 * Refreshes get handles by provided function.
		 * 
		 * @param {@function} func 
		 */
		setUpdater(func) {
			const implementation = new SimpleRefresher(func);
			this._enableUpdater(implementation);
		}

		/**
		 * Refresh gets handeled by provided Datatable.
		 * 
		 * @param {DataTable} dataTable 
		 */
		setUpdaterDataTablesXhr(dataTable) {
			this._enableUpdater(new DataTablesXhrRefresher(dataTable));
		}

		/**
		 * Manually trigger a refresh.
		 */
		onRefreshOnce() {
			this._implementation.onRefreshOnce(this);
		}

		/**
		 * If automatic refreshs are currently active on this page.
		 * 
		 * @returns {boolean}
		 */
		isRepeatedActive() {
			return this._enabled && (this._localStorage.getItem('live_switch') ?? '1') === '1';
		}

		/**
		 * Set if refreshes are active. Only needed to be called if refresh method has been registered,
		 * but these won't actually find any new data. This is used e.g. once and ansible tasks is completed.
		 * 
		 * @param {boolean} on 
		 */
		setEnabled(on) {
			if (this._enabled === on)
				return;
			this._enabled = on;
			if (on) {
				this._refresh_button.classList.remove('disabled');
				this._live_switch.classList.remove('bg-secondary');
			} else {
				this._refresh_button.classList.add('disabled');
				this._live_switch.classList.add('bg-secondary');
			}
		}
	}
