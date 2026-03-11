from __future__ import annotations

from lufa.repository.api_repository import ApiRepository, LufaKeyError, TowerJobStats
from tests.integration.conftest import HostIntependantTowerJobStats


class TestLufaKeyError:
    """Tests calls in api_repository with unkown tasks, callbacks etc. give a LufaKeyError.

    This is to give a proper HTTP Error message instead of a Server Error 500. Currently Sqlite
    doesn't check these , but that might change in the future.
    """

    def test_add_callback(self, api_repository: ApiRepository):
        try:
            api_repository.add_callback("5e52f2bb-7905-4ca9-9bdc-000000003f8d", "ansible_host", "ok", "{}", "module")
        except LufaKeyError as ex:
            assert ex.args[2] == "ansible_uuid"

    def test_add_task(self, api_repository: ApiRepository):
        try:
            api_repository.add_task("5e52f2bb-7905-4ca9-9bdc-000000003f8d", 42, "task_name")
        except LufaKeyError as ex:
            assert ex.args[2] == "tower_job_id"

    def test_update_job_artifacts(self, api_repository: ApiRepository):
        try:
            api_repository.update_job(420, "2026-03-09T13:26:57Z", "{not json}")
        except LufaKeyError as ex:
            assert ex.args[2] == "artifacts"

    def test_update_job_tower_job_id(self, api_repository: ApiRepository):
        try:
            api_repository.update_job(420, "2026-03-09T13:26:57Z", "{}")
        except LufaKeyError as ex:
            assert ex.args[2] == "tower_job_id"

    def test_update_job_timestamp(self, api_repository: ApiRepository):
        try:
            api_repository.update_job(420, "not a timestamp", "{}")
        except LufaKeyError as ex:
            assert ex.args[2] == "end_time"

    def test_job_exists(self, api_repository: ApiRepository):
        assert not api_repository.job_exists(4242)

    def test_add_stats(self, api_repository: ApiRepository, single_any_stat: HostIntependantTowerJobStats):
        try:
            api_repository.add_stats(42069, stats=[TowerJobStats(ansible_host="Undertest", **single_any_stat)])
        except LufaKeyError as ex:
            assert ex.args[2] == "tower_job_id"
