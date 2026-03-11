import json
import logging
import sqlite3
from abc import ABC, abstractmethod
from typing import Optional, TypeAlias, TypedDict

from psycopg2.errors import ForeignKeyViolation, InvalidDatetimeFormat, InvalidTextRepresentation

from lufa.database import DatabaseManager, JobState, JSon, TimeStamp

logger = logging.getLogger(__name__)


UnixTimeStamp: TypeAlias = int


class LufaKeyError(KeyError):
    def __init__(self, key, value):
        super().__init__("{} is not a known {}", value, key)

    @property
    def msg(self) -> str:
        return self.args[0].format(self.args[1], self.args[2])


class Callback(TypedDict):
    task_ansible_uuid: str
    ansible_host: str
    state: JobState
    module: str
    result_dump: str


class Task(TypedDict):
    ansible_uuid: str
    tower_job_id: int
    task_name: str


class TowerJobStats(TypedDict):
    ansible_host: str
    ok: int
    failed: int
    unreachable: int
    changed: int
    skipped: int
    rescued: int
    ignored: int


class JobTemplateComplianceStates(TypedDict):
    last_successful: UnixTimeStamp
    last_job_run: int
    compliance_interval_in_days: int
    playbook: str
    template_name: str
    tower_job_template_id: int
    organisation: str


class ApiRepository(ABC):
    @abstractmethod
    def get_all_noncompliant_hosts(self) -> dict[str, list[JobTemplateComplianceStates]]:
        """ "
        json structure:

        { hostname_fqdm: [{
            'last_successful': unix_timestamp ? 0
            'last_job_run': int_job_id
            'compliance_interval_in_days': int_num_days
            'playbook': str
            'template_name': str
            'tower_job_template_id': int
            'oranisation': str_tower
        }]}
        """
        pass

    @abstractmethod
    def update_job(
        self, tower_job_id: int, end_time: Optional[TimeStamp] = None, artifacts: Optional[JSon] = None
    ) -> None:
        pass

    @abstractmethod
    def job_exists(self, tower_job_id: int) -> bool:
        """Checks if a job exists."""
        pass

    @abstractmethod
    def add_job(
        self,
        tower_job_id: int,
        tower_job_template_id: int,
        tower_job_template_name: str,
        awx_tags: list[str],
        extra_vars: JSon,
        artifacts: JSon,
        ansible_limit: Optional[str] = None,
        tower_user_name: Optional[str] = None,
        tower_schedule_id: Optional[int] = None,
        tower_schedule_name: Optional[str] = None,
        tower_workflow_job_id: Optional[int] = None,
        tower_workflow_job_name: Optional[str] = None,
        compliance_interval: int = 0,
        template_infos: Optional[str] = None,
        playbook_path: Optional[str] = None,
        awx_organisation: Optional[str] = None,
        start_time: Optional[TimeStamp] = None,
    ) -> None:
        pass

    @abstractmethod
    def add_callback(
        self,
        task_ansible_uuid: str,
        ansible_host: str,
        state: JobState,
        result_dump: JSon,
        module: str,
        timestamp: Optional[str] = None,
    ) -> None:
        pass

    @abstractmethod
    def tasks_exists(self, task_uuid: str) -> bool:
        pass

    @abstractmethod
    def add_task(self, ansible_uuid: str, tower_job_id: int, task_name: str) -> None:
        pass

    @abstractmethod
    def add_stats(self, tower_job_id: int, stats: list[TowerJobStats]) -> None:
        pass


class SqliteApiRepository(ApiRepository):
    def __init__(self, db_manager: DatabaseManager) -> None:
        self.db_manager = db_manager
        self.callbacks: list = []

    def get_all_noncompliant_hosts(self) -> dict[str, list[JobTemplateComplianceStates]]:
        conn = self.db_manager.get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
                    SELECT
                        ansible_host,
                        noncompliant
                    FROM v_host_noncompliance
                """)
        ret: dict[str, list[JobTemplateComplianceStates]] = {}
        for line in cursor.fetchall():
            ret[line["ansible_host"]] = json.loads(line["noncompliant"])
        return ret

    def add_stats(self, tower_job_id: int, stats: list[TowerJobStats]) -> None:
        conn: sqlite3.Connection = self.db_manager.get_db_connection()
        cursor = conn.cursor()

        for stat in stats:
            cursor.execute(
                """
                            INSERT INTO stats (
                                tower_job_id, 
                                ansible_host, 
                                ok, 
                                failed, 
                                unreachable, 
                                changed,
                                skipped,
                                rescued,
                                ignored
                            )
                            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                            ON CONFLICT DO NOTHING
                        """,
                (
                    tower_job_id,
                    stat["ansible_host"],
                    stat["ok"],
                    stat["failed"],
                    stat["unreachable"],
                    stat["changed"],
                    stat["skipped"],
                    stat["rescued"],
                    stat["ignored"],
                ),
            )

        conn.commit()

    def add_callback(
        self,
        task_ansible_uuid: str,
        ansible_host: str,
        state: JobState,
        result_dump: JSon,
        module: str,
        timestamp: Optional[str] = None,
    ) -> None:
        conn: sqlite3.Connection = self.db_manager.get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            """
                            INSERT INTO task_callbacks (task_ansible_uuid, ansible_host, state, module, result_dump)
                            VALUES (?, ?, ?, ?, ?)
                        """,
            (
                task_ansible_uuid,
                ansible_host,
                state,
                module,
                result_dump,
            ),
        )
        # set timestamp if given and not None
        if timestamp is not None:
            cursor.execute(
                """
                                UPDATE task_callbacks
                                SET timestamp = ?
                                WHERE task_ansible_uuid = ?
                            """,
                (timestamp, task_ansible_uuid),
            )

        conn.commit()

    def job_exists(self, tower_job_id: int) -> bool:
        conn: sqlite3.Connection = self.db_manager.get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            """
                        SELECT *
                        FROM jobs
                        WHERE tower_job_id = ?
                        """,
            (tower_job_id,),
        )

        return cursor.fetchone() is not None

    def add_job(
        self,
        tower_job_id: int,
        tower_job_template_id: int,
        tower_job_template_name: str,
        awx_tags: list[str],
        extra_vars: JSon,
        artifacts: JSon,
        ansible_limit: Optional[str] = None,
        tower_user_name: Optional[str] = None,
        tower_schedule_id: Optional[int] = None,
        tower_schedule_name: Optional[str] = None,
        tower_workflow_job_id: Optional[int] = None,
        tower_workflow_job_name: Optional[str] = None,
        compliance_interval: int = 0,
        template_infos: Optional[str] = None,
        playbook_path: Optional[str] = None,
        awx_organisation: Optional[str] = None,
        start_time: Optional[TimeStamp] = None,
    ) -> None:
        conn: sqlite3.Connection = self.db_manager.get_db_connection()
        cursor = conn.cursor()

        # upsert job_template
        cursor.execute(
            """
                        INSERT INTO job_templates
                            (tower_job_template_id, tower_job_template_name, template_infos, playbook_path, awx_organisation, compliance_interval)
                        VALUES (?, ?, ?, ?, ?, ?)
                        ON CONFLICT (tower_job_template_id) DO UPDATE
                        SET (tower_job_template_name, template_infos, playbook_path, awx_organisation, compliance_interval) = (?, ?, ?, ?, ?)
                        """,
            (
                tower_job_template_id,
                tower_job_template_name,
                template_infos,
                playbook_path,
                awx_organisation,
                compliance_interval,
                tower_job_template_name,
                template_infos,
                playbook_path,
                awx_organisation,
                compliance_interval,
            ),
        )

        # insert job
        cursor.execute(
            """
                        INSERT INTO jobs (
                            tower_job_id,
                            tower_job_template_id,
                            ansible_limit,
                            tower_user_name,
                            awx_tags,
                            extra_vars,
                            artifacts,
                            tower_schedule_id,
                            tower_schedule_name,
                            tower_workflow_job_id,
                            tower_workflow_job_name
                        )
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                        """,
            (
                tower_job_id,
                tower_job_template_id,
                ansible_limit,
                tower_user_name,
                ",".join(awx_tags),
                extra_vars,
                artifacts,
                tower_schedule_id,
                tower_schedule_name,
                tower_workflow_job_id,
                tower_workflow_job_name,
            ),
        )
        # change start time if given and not None
        if start_time is not None:
            cursor.execute(
                """UPDATE jobs
                        SET start_time = ?
                    WHERE tower_job_id = ?
                """,
                (start_time, tower_job_id),
            )

        conn.commit()

    def add_task(self, ansible_uuid: str, tower_job_id: int, task_name: str) -> None:
        conn: sqlite3.Connection = self.db_manager.get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            """
                            INSERT INTO tasks (ansible_uuid, tower_job_id, task_name)
                            VALUES (?, ?, ?)
                        """,
            (ansible_uuid, tower_job_id, task_name),
        )
        conn.commit()

    def tasks_exists(self, task_uuid: str) -> bool:
        conn: sqlite3.Connection = self.db_manager.get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            """
                    SELECT *
                    FROM tasks
                    WHERE ansible_uuid = ?
                """,
            (task_uuid,),
        )
        return cursor.fetchone() is not None

    def update_job(
        self, tower_job_id: int, end_time: Optional[TimeStamp] = None, artifacts: Optional[JSon] = None
    ) -> None:
        conn: sqlite3.Connection = self.db_manager.get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            """
                    UPDATE jobs
                    SET
                        end_time = COALESCE(?, datetime('now','localtime')),
                        artifacts = COALESCE(?, '{}')
                    WHERE tower_job_id = ?
                    """,
            (
                end_time,
                artifacts,
                tower_job_id,
            ),
        )

        conn.commit()


class PostgresApiRepository(ApiRepository):
    def __init__(self, db_manager: DatabaseManager):
        self.db_manager = db_manager

    def get_all_noncompliant_hosts(self) -> dict[str, list[JobTemplateComplianceStates]]:
        conn = self.db_manager.get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
                SELECT
                    *
                FROM v_host_noncompliance
                """)
        ret = {}
        for line in cursor.fetchall():
            ret[line["ansible_host"]] = line["noncompliant"]
        return ret

    def job_exists(self, tower_job_id) -> bool:
        conn = self.db_manager.get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            """
                        SELECT *
                        FROM jobs
                        WHERE tower_job_id = %s
                        """,
            (tower_job_id,),
        )

        return cursor.rowcount != 0

    def add_job(
        self,
        tower_job_id: int,
        tower_job_template_id: int,
        tower_job_template_name: str,
        awx_tags: list[str],
        extra_vars: JSon,
        artifacts: JSon,
        ansible_limit: Optional[str] = None,
        tower_user_name: Optional[str] = None,
        tower_schedule_id: Optional[int] = None,
        tower_schedule_name: Optional[str] = None,
        tower_workflow_job_id: Optional[int] = None,
        tower_workflow_job_name: Optional[str] = None,
        compliance_interval: int = 0,
        template_infos: Optional[str] = None,
        playbook_path: Optional[str] = None,
        awx_organisation: Optional[str] = None,
        start_time: Optional[TimeStamp] = None,
    ) -> None:
        conn = self.db_manager.get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            """
                        INSERT INTO job_templates
                            (tower_job_template_id, tower_job_template_name, template_infos, playbook_path, awx_organisation, compliance_interval)
                        VALUES (%s, %s, %s, %s, %s, %s)
                        ON CONFLICT (tower_job_template_id) DO UPDATE
                            SET (tower_job_template_name, template_infos, playbook_path, awx_organisation, compliance_interval) = (%s, %s, %s, %s, %s)
                        """,
            (
                tower_job_template_id,
                tower_job_template_name,
                template_infos,
                playbook_path,
                awx_organisation,
                compliance_interval,
                tower_job_template_name,
                template_infos,
                playbook_path,
                awx_organisation,
                compliance_interval,
            ),
        )

        # insert job
        cursor.execute(
            """
                        INSERT INTO jobs (
                            tower_job_id,
                            tower_job_template_id,
                            ansible_limit,
                            tower_user_name,
                            awx_tags,
                            extra_vars,
                            artifacts,
                            tower_schedule_id,
                            tower_schedule_name,
                            tower_workflow_job_id,
                            tower_workflow_job_name
                        )
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                        """,
            (
                tower_job_id,
                tower_job_template_id,
                ansible_limit,
                tower_user_name,
                json.dumps(awx_tags),
                extra_vars,
                artifacts,
                tower_schedule_id,
                tower_schedule_name,
                tower_workflow_job_id,
                tower_workflow_job_name,
            ),
        )

        # set start_time if given and not null
        if start_time is not None:
            cursor.execute(
                """UPDATE jobs
                        SET start_time = %s
                    WHERE tower_job_id = %s
                """,
                (start_time, tower_job_id),
            )

        conn.commit()

    def add_callback(
        self,
        task_ansible_uuid: str,
        ansible_host: str,
        state: JobState,
        result_dump: JSon,
        module: str,
        timestamp: Optional[str] = None,
    ) -> None:
        conn = self.db_manager.get_db_connection()
        cursor = conn.cursor()
        try:
            cursor.execute(
                """
                    INSERT INTO task_callbacks (task_ansible_uuid, ansible_host, state, module, result_dump)
                    VALUES (%s, %s, %s, %s, %s)
                                    """,
                (task_ansible_uuid, ansible_host, state, module, result_dump),
            )
        except ForeignKeyViolation as ex:
            raise LufaKeyError("ansible_uuid", task_ansible_uuid) from ex

        # set timestamp if given and not None
        if timestamp is not None:
            cursor.execute(
                """
                                UPDATE task_callbacks
                                SET timestamp = ?
                                WHERE task_ansible_uuid = ?
                            """,
                (timestamp, task_ansible_uuid),
            )
        conn.commit()

    def tasks_exists(self, task_uuid: str) -> bool:
        conn = self.db_manager.get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            """
                    SELECT *
                    FROM tasks
                    WHERE ansible_uuid = %s
                """,
            (task_uuid,),
        )

        return cursor.rowcount > 0

    def add_task(self, ansible_uuid: str, tower_job_id: int, task_name: str) -> None:
        conn = self.db_manager.get_db_connection()
        cursor = conn.cursor()
        try:
            cursor.execute(
                """
                        INSERT INTO tasks (ansible_uuid, tower_job_id, task_name)
                        VALUES (%s, %s, %s)
                        """,
                (ansible_uuid, tower_job_id, task_name),
            )
        except ForeignKeyViolation as ex:
            raise LufaKeyError("tower_job_id", tower_job_id) from ex

        conn.commit()

    def add_stats(self, tower_job_id: int, stats: list[TowerJobStats]) -> None:
        conn = self.db_manager.get_db_connection()
        cursor = conn.cursor()

        try:
            for stat in stats:
                cursor.execute(
                    """
                                        INSERT INTO stats (
                                            tower_job_id,
                                            ansible_host,
                                            ok,
                                            failed,
                                            unreachable,
                                            changed,
                                            skipped,
                                            rescued,
                                            ignored
                                        )
                                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                                        ON CONFLICT DO NOTHING
                                    """,
                    (
                        tower_job_id,
                        stat["ansible_host"],
                        stat["ok"],
                        stat["failed"],
                        stat["unreachable"],
                        stat["changed"],
                        stat["skipped"],
                        stat["rescued"],
                        stat["ignored"],
                    ),
                )
            cursor.execute("REFRESH MATERIALIZED VIEW v_host_templates;")
        except ForeignKeyViolation as ex:
            raise LufaKeyError("tower_job_id", tower_job_id) from ex

        conn.commit()

    def update_job(
        self, tower_job_id: int, end_time: Optional[TimeStamp] = None, artifacts: Optional[JSon] = None
    ) -> None:
        with self.db_manager.get_db_connection() as db_conn:
            cur = db_conn.cursor()
            try:
                cur.execute(
                    """
                            UPDATE jobs
                            SET
                                end_time = COALESCE(%s, now()),
                                artifacts = COALESCE(%s, '{}'::jsonb)
                            WHERE tower_job_id = %s
                            """,
                    (
                        end_time,
                        artifacts,
                        tower_job_id,
                    ),
                )
            except InvalidTextRepresentation as ex:
                raise LufaKeyError("artifacts", artifacts) from ex
            except InvalidDatetimeFormat as ex:
                raise LufaKeyError("end_time", end_time) from ex
            except ForeignKeyViolation as ex:
                raise LufaKeyError("tower_job_id", tower_job_id) from ex
            db_conn.commit()
