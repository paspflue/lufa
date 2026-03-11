/**
 * Creates a DataTables button config that copies host limit values.
 *
 * @returns {object} DataTables button configuration.
 */
function getHostLimitButtonConfig() {
    return {
        text: 'Limit',
        action: (e, dt, node, config) => {
            let ansible_hosts = [];
            dt.rows({ search: 'applied' }).data().each((value, index) => {
                let split = value.ansible_host.split('.');
                let host_name = split.length < 1 ? value.ansible_host : split[0];
                ansible_hosts.push(host_name);
            });

            let limit = ansible_hosts.join(':');

            navigator.clipboard.writeText(limit);
        }
    };
}
