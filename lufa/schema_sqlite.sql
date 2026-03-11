CREATE TABLE IF NOT EXISTS lufa_users (
	distinguished_name varchar PRIMARY KEY,
	username varchar,
	data jsonb
);

CREATE TABLE IF NOT EXISTS job_templates (
	tower_job_template_id integer PRIMARY KEY,
	tower_job_template_name varchar,
	playbook_path varchar,
	compliance_interval integer DEFAULT 0,
	awx_organisation varchar,
	template_infos jsonb
);

CREATE TABLE IF NOT EXISTS jobs (
	tower_job_id integer PRIMARY KEY,
	tower_job_template_id integer REFERENCES job_templates ON DELETE RESTRICT,
	ansible_limit varchar,
	tower_user_name varchar,
	awx_tags jsonb,
	extra_vars jsonb default '{}',
	artifacts jsonb default '{}',
	tower_schedule_id integer,
	tower_schedule_name varchar,
	tower_workflow_job_id integer,
	tower_workflow_job_name varchar,
	start_time datetime DEFAULT (datetime('now','localtime')),
	end_time datetime
);

CREATE TABLE IF NOT EXISTS stats (
	tower_job_id integer REFERENCES jobs ON DELETE CASCADE,
	ansible_host varchar,
	ok integer,
	failed integer,
	unreachable integer,
	changed integer,
	skipped integer,
	rescued integer,
	ignored integer,
	PRIMARY KEY (tower_job_id, ansible_host)
);

CREATE TABLE IF NOT EXISTS tasks (
	ansible_uuid uuid PRIMARY KEY,
	tower_job_id integer REFERENCES jobs ON DELETE CASCADE,
	task_name varchar
);

CREATE TABLE IF NOT EXISTS task_callbacks (
	id integer PRIMARY KEY AUTOINCREMENT,
	task_ansible_uuid uuid REFERENCES tasks ON DELETE CASCADE,
	ansible_host varchar,
	state varchar,
	module varchar,
	timestamp datetime DEFAULT (strftime('%Y-%m-%d %H:%M:%f', 'now', 'localtime')),
	result_dump jsonb
);

CREATE INDEX IF NOT EXISTS stats_ansible_host_index ON stats (ansible_host);
CREATE INDEX IF NOT EXISTS jobs_tower_job_template_id_index ON jobs (tower_job_template_id);
CREATE INDEX IF NOT EXISTS jobs_start_time_index ON jobs (start_time);
CREATE INDEX IF NOT EXISTS tasks_tower_job_id_index ON tasks (tower_job_id);
CREATE INDEX IF NOT EXISTS task_callbacks_task_uuid_index ON task_callbacks (task_ansible_uuid);
CREATE INDEX IF NOT EXISTS task_callbacks_ansible_host_index ON task_callbacks (ansible_host);
CREATE INDEX IF NOT EXISTS task_callbacks_timestamp_index ON task_callbacks (timestamp);
CREATE INDEX IF NOT EXISTS task_callbacks_state_index ON task_callbacks (state);


CREATE VIEW IF NOT EXISTS v_tower_job_stats AS
SELECT
	stats.*,
	tower_job_template_name,
	awx_tags,
	start_time,
	compliance_interval
FROM stats
JOIN jobs
  ON stats.tower_job_id = jobs.tower_job_id
JOIN job_templates
  ON jobs.tower_job_template_id = job_templates.tower_job_template_id;

CREATE VIEW IF NOT EXISTS v_last_tower_job_callbacks AS
SELECT
	id,
	task_name,
	ansible_host,
	state,
	max(timestamp),
	tower_job_id
FROM task_callbacks
JOIN tasks
  ON tasks.ansible_uuid = task_callbacks.task_ansible_uuid
GROUP BY tasks.tower_job_id
ORDER BY tasks.tower_job_id DESC;

CREATE VIEW IF NOT EXISTS v_job_status AS
    SELECT
        jobs.*,
        CASE
            WHEN jobs.end_time IS NULL
                AND datetime(jobs.start_time) < datetime(current_timestamp, '-24 HOURS')
                THEN 'error'
            WHEN jobs.end_time IS NULL THEN 'started'
            WHEN EXISTS (
                    SELECT 1 FROM stats
                        WHERE jobs.tower_job_id = stats.tower_job_id
		                    AND (failed > 0 OR unreachable > 0)) THEN 'failed'
            ELSE 'success'
        END as state
    FROM jobs;

CREATE VIEW IF NOT EXISTS v_host_templates AS	
    SELECT DISTINCT
		ansible_host,
        job_templates.tower_job_template_id,
        job_templates.tower_job_template_name,
        awx_tags,
        (start_time >= datetime(current_timestamp, concat('-', compliance_interval, ' DAYS'))
             AND failed=0 AND unreachable = 0
             OR compliance_interval = 0) AS compliant,
        (failed=0 AND unreachable=0) AS successful,
        start_time,
        compliance_interval,
        jobs.tower_job_id,
        awx_organisation,
        playbook_path
    FROM stats
    JOIN jobs
    ON stats.tower_job_id = jobs.tower_job_id
    JOIN job_templates
    ON jobs.tower_job_template_id = job_templates.tower_job_template_id;

CREATE VIEW IF NOT EXISTS v_host_template_compliance AS
	SELECT
		ansible_host,
		tower_job_template_id,
		tower_job_template_name,   -- implicit first
		compliance_interval,       -- implicit first
		playbook_path,             -- implicit first
		awx_organisation,          -- implicit first
		MAX(compliant) AS template_compliant
	FROM v_host_templates
	GROUP BY ansible_host, tower_job_template_id;

CREATE VIEW IF NOT EXISTS v_host_compliance AS
	SELECT
		ansible_host,
		MIN(template_compliant) AS compliant
	FROM v_host_template_compliance
	GROUP BY ansible_host;

CREATE VIEW IF NOT EXISTS v_template_compliance AS
	SELECT
		tower_job_template_id,
		(SELECT json_group_array(ansible_host)) AS noncompliant
	FROM v_host_template_compliance
	WHERE NOT template_compliant
	GROUP BY tower_job_template_id;

CREATE VIEW IF NOT EXISTS v_host_noncompliance AS
	SELECT
		ansible_host,
		(SELECT json_group_array(json_object(
			'last_successful', (SELECT COALESCE(cast(strftime('%s', MAX(start_time)) AS INTEGER), 0)
								FROM v_host_templates_ordered AS ordered
								WHERE compliance.tower_job_template_id = ordered.tower_job_template_id
									AND compliance.ansible_host = ordered.ansible_host
									AND ordered.successful),
			'last_job_run', (SELECT MAX(tower_job_id)
							 FROM v_host_templates_ordered AS ordered
							 WHERE compliance.tower_job_template_id = ordered.tower_job_template_id
								AND compliance.ansible_host = ordered.ansible_host),
 			'compliance_interval_in_days', compliance_interval,
			'playbook', playbook_path,
			'template_name', tower_job_template_name,
			'tower_job_template_id', tower_job_template_id,
			'organisation', awx_organisation))
		) AS noncompliant
	FROM v_host_template_compliance AS compliance
	WHERE NOT template_compliant
	GROUP BY ansible_host;

CREATE VIEW IF NOT EXISTS v_host_templates_ordered AS
	SELECT
	    ansible_host,
	    awx_tags,
	    compliance_interval,
	    compliant,
	    start_time,
	    tower_job_id,
		tower_job_template_id,
		successful
	FROM v_host_templates
	ORDER BY ansible_host, tower_job_template_id, successful DESC, start_time DESC;

CREATE VIEW IF NOT EXISTS v_template_hosts_summary AS
	SELECT
	    ansible_host,
	    awx_tags,  -- implicit first()
	    compliance_interval,  -- implicit first()
	    compliant,  -- implicit first()
	    start_time,  -- implicit first()
	    tower_job_id,  -- implicit first()
		tower_job_template_id
	FROM v_host_templates_ordered
	GROUP BY ansible_host, tower_job_template_id;
