from datetime import timedelta

from lufa.repository.backend_repository import BackendRepository
from tests.integration.conftest import HostIntependantTowerJobStats, LufaFactory


class TestGetJobStatus:
    HOST_UNDER_TEST = "HostUnderTest"

    def test_job_without_stats_started_less_than_24h_ago_is_started(
        self, backend_repository: BackendRepository, lufa_factory: LufaFactory
    ):
        job = lufa_factory.add_tower_template().add_job(started_ago=timedelta(hours=23))

        ret = backend_repository.get_job_status(job.tower_job_id)

        assert ret["state"] == "started"

    def test_job_without_stats_started_more_than_24h_ago_is_error(
        self, backend_repository: BackendRepository, lufa_factory: LufaFactory
    ):
        job = lufa_factory.add_tower_template().add_job(started_ago=timedelta(hours=26))

        ret = backend_repository.get_job_status(job.tower_job_id)

        assert ret["state"] == "error"

    def test_single_failed_status(
        self,
        backend_repository: BackendRepository,
        lufa_factory: LufaFactory,
        failed_stat: HostIntependantTowerJobStats,
    ):
        job = lufa_factory.add_tower_template().add_job().with_stats(self.HOST_UNDER_TEST, failed_stat).with_end_time()

        ret = backend_repository.get_job_status(job.tower_job_id)

        assert ret["state"] == "failed"

    def test_single_success_status(
        self,
        backend_repository: BackendRepository,
        lufa_factory: LufaFactory,
        success_stat: HostIntependantTowerJobStats,
    ):
        job = lufa_factory.add_tower_template().add_job().with_stats(self.HOST_UNDER_TEST, success_stat).with_end_time()

        ret = backend_repository.get_job_status(job.tower_job_id)

        assert ret["state"] == "success"

    def test_previous_failed_does_not_changed_current_success(
        self,
        backend_repository: BackendRepository,
        lufa_factory: LufaFactory,
        success_stat: HostIntependantTowerJobStats,
        failed_stat: HostIntependantTowerJobStats,
    ):
        template = lufa_factory.add_tower_template()
        template.add_job().with_stats(self.HOST_UNDER_TEST, failed_stat).with_end_time()
        job = template.add_job().with_stats(self.HOST_UNDER_TEST, success_stat).with_end_time()

        ret = backend_repository.get_job_status(job.tower_job_id)

        assert ret["state"] == "success"

    def test_previous_success_does_not_changed_current_failed(
        self,
        backend_repository: BackendRepository,
        lufa_factory: LufaFactory,
        success_stat: HostIntependantTowerJobStats,
        failed_stat: HostIntependantTowerJobStats,
    ):
        template = lufa_factory.add_tower_template()
        template.add_job().with_stats(self.HOST_UNDER_TEST, success_stat).with_end_time()
        job = template.add_job().with_stats(self.HOST_UNDER_TEST, failed_stat).with_end_time()

        ret = backend_repository.get_job_status(job.tower_job_id)

        assert ret["state"] == "failed"

    def test_future_failed_does_not_changed_current_success(
        self,
        backend_repository: BackendRepository,
        lufa_factory: LufaFactory,
        success_stat: HostIntependantTowerJobStats,
        failed_stat: HostIntependantTowerJobStats,
    ):
        template = lufa_factory.add_tower_template()
        job = template.add_job().with_stats(self.HOST_UNDER_TEST, success_stat).with_end_time()
        template.add_job().with_stats(self.HOST_UNDER_TEST, failed_stat).with_end_time()

        ret = backend_repository.get_job_status(job.tower_job_id)

        assert ret["state"] == "success"

    def test_future_success_does_not_changed_current_failed(
        self,
        backend_repository: BackendRepository,
        lufa_factory: LufaFactory,
        success_stat: HostIntependantTowerJobStats,
        failed_stat: HostIntependantTowerJobStats,
    ):
        template = lufa_factory.add_tower_template()
        job = template.add_job().with_stats(self.HOST_UNDER_TEST, failed_stat).with_end_time()
        template.add_job().with_stats(self.HOST_UNDER_TEST, success_stat).with_end_time()

        ret = backend_repository.get_job_status(job.tower_job_id)

        assert ret["state"] == "failed"

    def test_mix_failed_and_success_is_failed(
        self,
        backend_repository: BackendRepository,
        lufa_factory: LufaFactory,
        success_stat: HostIntependantTowerJobStats,
        failed_stat: HostIntependantTowerJobStats,
    ):
        template = lufa_factory.add_tower_template()
        template.add_job().with_stats(self.HOST_UNDER_TEST, success_stat).with_end_time()
        job = (
            template.add_job()
            .with_stats("firstHost", success_stat)
            .with_stats(self.HOST_UNDER_TEST, failed_stat)
            .with_stats("lastHost", success_stat)
            .with_end_time()
        )

        ret = backend_repository.get_job_status(job.tower_job_id)

        assert ret["state"] == "failed"
