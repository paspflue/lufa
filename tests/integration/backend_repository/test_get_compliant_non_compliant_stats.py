from __future__ import annotations

from datetime import timedelta

from lufa.repository.backend_repository import BackendRepository
from tests.integration.conftest import HostIntependantTowerJobStats, LufaFactory


class TestGetCompliantNonCompliantStats:
    HOST_UNDER_TEST = "HostUnderTest"

    def test_empty_repository(self, backend_repository: BackendRepository):
        ret = backend_repository.get_compliant_non_compliant_stats()
        assert ret == {"compliant": 0, "not_compliant": 0}

    def test_compliant_with_all_tower_templates_have_compliance_interval_zero(
        self,
        backend_repository: BackendRepository,
        lufa_factory: LufaFactory,
        any_stat: HostIntependantTowerJobStats,
    ):
        lufa_factory.add_tower_template().add_job_with_compliance_interval(0).with_stats(self.HOST_UNDER_TEST, any_stat)

        ret = backend_repository.get_compliant_non_compliant_stats()

        assert ret == {"compliant": 1, "not_compliant": 0}

    def test_non_compliant_with_only_failed_runs_and_positive_compliance_interval(
        self,
        backend_repository: BackendRepository,
        lufa_factory: LufaFactory,
        failed_stat: HostIntependantTowerJobStats,
    ):
        lufa_factory.add_tower_template().add_job_with_compliance_interval(3).with_stats(
            self.HOST_UNDER_TEST, failed_stat
        )

        ret = backend_repository.get_compliant_non_compliant_stats()

        assert ret == {"compliant": 0, "not_compliant": 1}

    def test_successful_run_within_positive_compliance_interval_is_compliant(
        self,
        backend_repository: BackendRepository,
        lufa_factory: LufaFactory,
        success_stat: HostIntependantTowerJobStats,
    ):
        lufa_factory.add_tower_template().add_job_with_compliance_interval(3).with_stats(
            self.HOST_UNDER_TEST, success_stat
        )

        ret = backend_repository.get_compliant_non_compliant_stats()

        assert ret == {"compliant": 1, "not_compliant": 0}

    def test_successful_run_outside_positive_compliance_interval_is_non_compliant(
        self,
        backend_repository: BackendRepository,
        lufa_factory: LufaFactory,
        success_stat: HostIntependantTowerJobStats,
    ):
        lufa_factory.add_tower_template().add_job_with_compliance_interval(3, started_ago=timedelta(days=4)).with_stats(
            self.HOST_UNDER_TEST, success_stat
        )

        ret = backend_repository.get_compliant_non_compliant_stats()

        assert ret == {"compliant": 0, "not_compliant": 1}

    def test_only_failed_runs_within_positive_compliance_interval_is_noncompliant(
        self,
        backend_repository: BackendRepository,
        lufa_factory: LufaFactory,
        success_stat: HostIntependantTowerJobStats,
        failed_stat: HostIntependantTowerJobStats,
    ):
        template = lufa_factory.add_tower_template()
        template.add_job_with_compliance_interval(3, started_ago=timedelta(days=4)).with_stats(
            self.HOST_UNDER_TEST, success_stat
        )
        template.add_job_with_compliance_interval(3, started_ago=timedelta(days=2)).with_stats(
            self.HOST_UNDER_TEST, failed_stat
        )

        ret = backend_repository.get_compliant_non_compliant_stats()

        assert ret == {"compliant": 0, "not_compliant": 1}

    def test_mixture_of_failed_and_successful_runs_within_positive_compliance_interval_is_compliant(
        self,
        backend_repository: BackendRepository,
        lufa_factory: LufaFactory,
        success_stat: HostIntependantTowerJobStats,
        failed_stat: HostIntependantTowerJobStats,
    ):
        template = lufa_factory.add_tower_template()
        template.add_job_with_compliance_interval(3, started_ago=timedelta(days=2)).with_stats(
            self.HOST_UNDER_TEST, success_stat
        )
        template.add_job_with_compliance_interval(3, started_ago=timedelta(days=2)).with_stats(
            self.HOST_UNDER_TEST, failed_stat
        )

        ret = backend_repository.get_compliant_non_compliant_stats()

        assert ret == {"compliant": 1, "not_compliant": 0}

    def test_mixture_of_failed_and_successful_runs_within_positive_compliance_interval_is_compliant_before(
        self,
        backend_repository: BackendRepository,
        lufa_factory: LufaFactory,
        success_stat: HostIntependantTowerJobStats,
        failed_stat: HostIntependantTowerJobStats,
    ):
        template = lufa_factory.add_tower_template()
        template.add_job_with_compliance_interval(3, started_ago=timedelta(days=2)).with_stats(
            self.HOST_UNDER_TEST, success_stat
        )
        template.add_job_with_compliance_interval(3, started_ago=timedelta(days=1)).with_stats(
            self.HOST_UNDER_TEST, failed_stat
        )

        ret = backend_repository.get_compliant_non_compliant_stats()

        assert ret == {"compliant": 1, "not_compliant": 0}

    def test_mixture_of_failed_and_successful_runs_within_positive_compliance_interval_is_compliant_after(
        self,
        backend_repository: BackendRepository,
        lufa_factory: LufaFactory,
        success_stat: HostIntependantTowerJobStats,
        failed_stat: HostIntependantTowerJobStats,
    ):
        template = lufa_factory.add_tower_template()
        template.add_job_with_compliance_interval(3, started_ago=timedelta(days=2)).with_stats(
            self.HOST_UNDER_TEST, failed_stat
        )
        template.add_job_with_compliance_interval(3, started_ago=timedelta(days=1)).with_stats(
            self.HOST_UNDER_TEST, success_stat
        )

        ret = backend_repository.get_compliant_non_compliant_stats()

        assert ret == {"compliant": 1, "not_compliant": 0}

    def test_each_host_has_own_compliance(
        self,
        backend_repository: BackendRepository,
        lufa_factory: LufaFactory,
        success_stat: HostIntependantTowerJobStats,
        failed_stat: HostIntependantTowerJobStats,
    ):
        other_host = "OtherHost"
        template = lufa_factory.add_tower_template()
        template.add_job_with_compliance_interval(3, started_ago=timedelta(days=2)).with_stats(
            self.HOST_UNDER_TEST, failed_stat
        )
        template.add_job_with_compliance_interval(3, started_ago=timedelta(days=2)).with_stats(other_host, success_stat)

        ret = backend_repository.get_compliant_non_compliant_stats()

        assert ret == {"compliant": 1, "not_compliant": 1}

    def test_each_host_has_own_compliance_both_compliant(
        self,
        backend_repository: BackendRepository,
        lufa_factory: LufaFactory,
        success_stat: HostIntependantTowerJobStats,
    ):
        other_host = "OtherHost"
        template = lufa_factory.add_tower_template()
        template.add_job_with_compliance_interval(3, started_ago=timedelta(days=2)).with_stats(
            self.HOST_UNDER_TEST, success_stat
        )
        template.add_job_with_compliance_interval(3, started_ago=timedelta(days=2)).with_stats(other_host, success_stat)

        ret = backend_repository.get_compliant_non_compliant_stats()

        assert ret == {"compliant": 2, "not_compliant": 0}

    def test_each_host_has_own_compliance_both_not_compliant(
        self,
        backend_repository: BackendRepository,
        lufa_factory: LufaFactory,
        failed_stat: HostIntependantTowerJobStats,
    ):
        other_host = "OtherHost"
        template = lufa_factory.add_tower_template()
        template.add_job_with_compliance_interval(3, started_ago=timedelta(days=2)).with_stats(
            self.HOST_UNDER_TEST, failed_stat
        )
        template.add_job_with_compliance_interval(3, started_ago=timedelta(days=2)).with_stats(other_host, failed_stat)

        ret = backend_repository.get_compliant_non_compliant_stats()

        assert ret == {"compliant": 0, "not_compliant": 2}

    def test_single_non_compliant_template_is_non_compliant(
        self,
        backend_repository: BackendRepository,
        lufa_factory: LufaFactory,
        any_stat: HostIntependantTowerJobStats,
        failed_stat: HostIntependantTowerJobStats,
    ):
        template_one = lufa_factory.add_tower_template()
        template_two = lufa_factory.add_tower_template()
        assert template_one.tower_job_template_id < template_two.tower_job_template_id
        template_one.add_job_with_compliance_interval(3, started_ago=timedelta(days=2)).with_stats(
            self.HOST_UNDER_TEST, failed_stat
        )
        template_two.add_job_with_compliance_interval(3, started_ago=timedelta(days=2)).with_stats(
            self.HOST_UNDER_TEST, any_stat
        )

        ret = backend_repository.get_compliant_non_compliant_stats()

        assert ret == {"compliant": 0, "not_compliant": 1}
