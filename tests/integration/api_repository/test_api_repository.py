import datetime
import uuid
from sqlite3 import Cursor

import pytest

from lufa.database import DatabaseManager, NewJob
from lufa.repository.api_repository import ApiRepository, Callback, Task, TowerJobStats

new_job: NewJob = {
    "tower_job_id": 1234,
    "tower_job_template_id": 124,
    "playbook_path": "test-play.yml",
    "tower_job_template_name": "Test Template",
    "ansible_limit": "unx1000:unx1001",
    "tower_user_name": "test_user",
    "awx_tags": [],
    "extra_vars": "{}",
    "artifacts": "{}",
    "tower_schedule_id": None,
    "tower_schedule_name": None,
    "tower_workflow_job_id": None,
    "tower_workflow_job_name": None,
    "compliance_interval": 0,
    "template_infos": None,
}

new_stats: list[TowerJobStats] = [
    {
        "ansible_host": "unx1010",
        "ok": 20,
        "failed": 2,
        "unreachable": 0,
        "changed": 6,
        "skipped": 3,
        "rescued": 0,
        "ignored": 0,
    },
    {
        "ansible_host": "unx1001",
        "ok": 25,
        "failed": 2,
        "unreachable": 0,
        "changed": 2,
        "skipped": 3,
        "rescued": 0,
        "ignored": 0,
    },
]

new_task: Task = {"ansible_uuid": str(uuid.uuid4()), "tower_job_id": new_job["tower_job_id"], "task_name": "Mein Task"}

test_callback: Callback = {
    "task_ansible_uuid": new_task["ansible_uuid"],
    "ansible_host": "unx1000",
    "state": "started",
    "module": "test_module",
    "result_dump": "{}",
}


class TestApiRepository:
    @pytest.mark.postgres
    def test_add_callback_postgres(self, api_repository: ApiRepository, db_manager: DatabaseManager):
        api_repository.add_job(**new_job)
        api_repository.add_task(**new_task)
        api_repository.add_callback(**test_callback)

        cursor = db_manager.get_db_connection().cursor()
        cursor.execute(
            """
            SELECT * FROM task_callbacks
            WHERE task_ansible_uuid = %s
        """,
            (test_callback["task_ansible_uuid"],),
        )

        assert cursor.fetchone() is not None

    @pytest.mark.sqlite3
    def test_add_callback_sqlite(self, api_repository: ApiRepository, db_manager: DatabaseManager):
        api_repository.add_callback(**test_callback)

        cursor: Cursor = db_manager.get_db_connection().cursor()
        cursor.execute(
            """
            SELECT * FROM task_callbacks
            WHERE task_ansible_uuid = ?
        """,
            (test_callback["task_ansible_uuid"],),
        )

        assert cursor.fetchone() is not None

    @pytest.mark.postgres
    def test_add_stats_postgres(self, api_repository: ApiRepository, db_manager: DatabaseManager):
        tower_job_id = new_job["tower_job_id"]

        api_repository.add_job(**new_job)

        api_repository.add_stats(tower_job_id, new_stats)

        cursor = db_manager.get_db_connection().cursor()
        cursor.execute(
            """
                    SELECT * FROM stats
                    WHERE tower_job_id = %s
                """,
            (tower_job_id,),
        )

        assert len(cursor.fetchall()) == len(new_stats)

    @pytest.mark.sqlite3
    def test_add_stats_sqlite(self, api_repository: ApiRepository, db_manager: DatabaseManager):
        tower_job_id = 1234

        api_repository.add_stats(tower_job_id, new_stats)

        cursor: Cursor = db_manager.get_db_connection().cursor()
        cursor.execute(
            """
                    SELECT * FROM stats
                    WHERE tower_job_id = ?
                """,
            (tower_job_id,),
        )

        assert len(cursor.fetchall()) == len(new_stats)

    def test_job_exists(self, api_repository: ApiRepository):
        assert not api_repository.job_exists(new_job["tower_job_id"])
        api_repository.add_job(**new_job)
        assert api_repository.job_exists(new_job["tower_job_id"])

    # wird bereits getestet in job_exists
    # def test_add_job(self, api_repository: ApiRepository):
    #     assert False

    # wird bereits getestet in tasks
    # def test_add_task(self, api_repository: ApiRepository):
    #     assert False

    def test_tasks_exists(self, api_repository: ApiRepository):
        assert not api_repository.tasks_exists(new_task["ansible_uuid"])
        api_repository.add_job(**new_job)

        api_repository.add_task(**new_task)
        assert api_repository.tasks_exists(new_task["ansible_uuid"])

    @pytest.mark.postgres
    def test_update_job_postgres(self, api_repository: ApiRepository, db_manager: DatabaseManager):
        api_repository.add_job(**new_job)

        api_repository.update_job(new_job["tower_job_id"])

        cursor = db_manager.get_db_connection().cursor()
        cursor.execute(
            """
                            SELECT * FROM jobs
                            WHERE tower_job_id = %s
                        """,
            (new_job["tower_job_id"],),
        )

        assert cursor.fetchone()["end_time"] is not None

    @pytest.mark.sqlite3
    def test_update_job_sqlite(self, api_repository: ApiRepository, db_manager: DatabaseManager):
        api_repository.add_job(**new_job)

        api_repository.update_job(new_job["tower_job_id"], end_time=None, artifacts=None)

        cursor: Cursor = db_manager.get_db_connection().cursor()
        cursor.execute(
            """
                            SELECT * FROM jobs
                            WHERE tower_job_id = ?
                        """,
            (new_job["tower_job_id"],),
        )
        job = cursor.fetchone()

        assert job["end_time"] is not None
        dt = datetime.datetime.now() - datetime.datetime.fromisoformat(job["end_time"])
        assert dt < datetime.timedelta(seconds=1)  # correct end_time
