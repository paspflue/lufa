DROP INDEX IF EXISTS jobs_tower_job_template_id_index;
DROP INDEX IF EXISTS jobs_start_time_index;
DROP INDEX IF EXISTS tasks_tower_job_id_index;
DROP INDEX IF EXISTS task_callbacks_task_uuid;
DROP INDEX IF EXISTS task_callbacks_ansible_host_index;
DROP INDEX IF EXISTS task_callbacks_timestamp_index;
DROP INDEX IF EXISTS stats_ansible_host_index;

-- DROP TRIGGER IF EXISTS delete_unreferenced_job_templates ON jobs;
-- DROP FUNCTION IF EXISTS delete_unreferenced_job_templates();

DROP TABLE IF EXISTS task_callbacks;
DROP TABLE IF EXISTS tasks;
DROP TABLE IF EXISTS lufa_job_vars; -- deprecated table
DROP TABLE IF EXISTS stats;
DROP TABLE IF EXISTS jobs;
DROP TABLE IF EXISTS job_templates;
DROP TABLE IF EXISTS lufa_users;