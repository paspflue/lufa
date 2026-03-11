from __future__ import annotations

from datetime import timedelta
from re import findall

from lufa.database import TimeStamp
from lufa.repository.backend_repository import BackendRepository
from tests.integration.conftest import HostIntependantTowerJobStats, LufaFactory


class TestGetHostTemplates:
    HOST_UNDER_TEST = "HostUnderTest"

    def test_empty_repository(self, backend_repository: BackendRepository):
        ret = backend_repository.get_host_templates(self.HOST_UNDER_TEST)
        assert len(ret) == 0

    def test_compliant_with_all_tower_templates_have_compliance_interval_zero(
        self,
        backend_repository: BackendRepository,
        lufa_factory: LufaFactory,
        any_stat: HostIntependantTowerJobStats,
    ):
        lufa_factory.add_tower_template().add_job_with_compliance_interval(0).with_stats(self.HOST_UNDER_TEST, any_stat)

        ret = backend_repository.get_host_templates(self.HOST_UNDER_TEST)

        assert len(ret) == 1
        assert ret[0]["compliant"]
        assert type(ret[0]["compliant"]) is bool
        assert type(ret[0]["start_time"]) is TimeStamp
        assert len(findall(r"^20\d\d-[01]\d-[0-3]\dT[0-2]\d:[0-5]\d:[0-5]\d.\d\d\d$", ret[0]["start_time"])) == 1, ret[
            0
        ]["start_time"]

    def test_non_compliant_with_only_failed_runs_and_positive_compliance_interval(
        self,
        backend_repository: BackendRepository,
        lufa_factory: LufaFactory,
        failed_stat: HostIntependantTowerJobStats,
    ):
        lufa_factory.add_tower_template().add_job_with_compliance_interval(3).with_stats(
            self.HOST_UNDER_TEST, failed_stat
        )

        ret = backend_repository.get_host_templates(self.HOST_UNDER_TEST)

        assert len(ret) == 1
        assert not ret[0]["compliant"]

    def test_successful_run_within_positive_compliance_interval_is_compliant(
        self,
        backend_repository: BackendRepository,
        lufa_factory: LufaFactory,
        success_stat: HostIntependantTowerJobStats,
    ):
        lufa_factory.add_tower_template().add_job_with_compliance_interval(3).with_stats(
            self.HOST_UNDER_TEST, success_stat
        )

        ret = backend_repository.get_host_templates(self.HOST_UNDER_TEST)

        expected = [{"compliant": True, "successful": True}]
        actual = [{k: v for (k, v) in r.items() if k in ["compliant", "successful"]} for r in ret]
        assert actual == expected

    def test_each_template_only_once(
        self,
        backend_repository: BackendRepository,
        lufa_factory: LufaFactory,
        success_stat: HostIntependantTowerJobStats,
    ):
        template = lufa_factory.add_tower_template()
        template.add_job_with_compliance_interval(3, started_ago=timedelta(days=2)).with_stats(
            self.HOST_UNDER_TEST, success_stat
        )
        last_job = template.add_job_with_compliance_interval(3, started_ago=timedelta(days=1))
        last_job.with_stats(self.HOST_UNDER_TEST, success_stat)

        ret = backend_repository.get_host_templates(self.HOST_UNDER_TEST)

        assert len(ret) == 1, ret
        assert ret[0]["tower_job_id"] == last_job.tower_job_id

    def test_each_template_has_own_line(
        self,
        backend_repository: BackendRepository,
        lufa_factory: LufaFactory,
        success_stat: HostIntependantTowerJobStats,
    ):
        lufa_factory.add_tower_template().add_job_with_compliance_interval(3, started_ago=timedelta(days=2)).with_stats(
            self.HOST_UNDER_TEST, success_stat
        )
        lufa_factory.add_tower_template().add_job_with_compliance_interval(3, started_ago=timedelta(days=1)).with_stats(
            self.HOST_UNDER_TEST, success_stat
        )

        ret = backend_repository.get_host_templates(self.HOST_UNDER_TEST)

        assert len(ret) == 2, ret

    def test_successful_run_outside_positive_compliance_interval_is_non_compliant(
        self,
        backend_repository: BackendRepository,
        lufa_factory: LufaFactory,
        success_stat: HostIntependantTowerJobStats,
    ):
        lufa_factory.add_tower_template().add_job_with_compliance_interval(3, started_ago=timedelta(days=4)).with_stats(
            self.HOST_UNDER_TEST, success_stat
        )

        ret = backend_repository.get_host_templates(self.HOST_UNDER_TEST)

        expected = [{"compliant": False, "successful": True}]
        actual = [{k: v for (k, v) in r.items() if k in ["compliant", "successful"]} for r in ret]
        assert actual == expected

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

        ret = backend_repository.get_host_templates(self.HOST_UNDER_TEST)

        expected = [{"compliant": False, "successful": False}]
        actual = [{k: v for (k, v) in r.items() if k in ["compliant", "successful"]} for r in ret]
        assert actual == expected

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

        ret = backend_repository.get_host_templates(self.HOST_UNDER_TEST)

        expected = [{"compliant": True, "successful": False}]
        actual = [{k: v for (k, v) in r.items() if k in ["compliant", "successful"]} for r in ret]
        assert actual == expected

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

        ret = backend_repository.get_host_templates(self.HOST_UNDER_TEST)

        expected = [{"compliant": True, "successful": False}]
        actual = [{k: v for (k, v) in r.items() if k in ["compliant", "successful"]} for r in ret]
        assert actual == expected

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

        ret = backend_repository.get_host_templates(self.HOST_UNDER_TEST)

        expected = [{"compliant": True, "successful": True}]
        actual = [{k: v for (k, v) in r.items() if k in ["compliant", "successful"]} for r in ret]
        assert actual == expected

    def test_mixture_of_failed_and_successful_runs_within_positive_compliance_interval_is_compliant_three_jobs(
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
        template.add_job_with_compliance_interval(3, started_ago=timedelta(days=0)).with_stats(
            self.HOST_UNDER_TEST, success_stat
        )

        ret = backend_repository.get_host_templates(self.HOST_UNDER_TEST)

        expected = [
            {"compliant": True, "successful": True},
        ]
        actual = [{k: v for (k, v) in r.items() if k in ["compliant", "successful"]} for r in ret]
        assert actual == expected

    def test_successful_run_on_different_host_does_not_change_non_compliance(
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
        template.add_job_with_compliance_interval(3, started_ago=timedelta(days=2)).with_stats(
            "OtherHost", success_stat
        )

        ret = backend_repository.get_host_templates(self.HOST_UNDER_TEST)

        expected = [{"compliant": False, "successful": False}]
        actual = [{k: v for (k, v) in r.items() if k in ["compliant", "successful"]} for r in ret]
        assert actual == expected

    def test_multible_templates_each_have_own_entry(
        self,
        backend_repository: BackendRepository,
        lufa_factory: LufaFactory,
        success_stat: HostIntependantTowerJobStats,
        failed_stat: HostIntependantTowerJobStats,
    ):
        template_one = lufa_factory.add_tower_template()
        template_two = lufa_factory.add_tower_template()
        assert template_one.tower_job_template_id < template_two.tower_job_template_id
        template_one.add_job_with_compliance_interval(3, started_ago=timedelta(days=2)).with_stats(
            self.HOST_UNDER_TEST, failed_stat
        )
        template_two.add_job_with_compliance_interval(3, started_ago=timedelta(days=2)).with_stats(
            self.HOST_UNDER_TEST, success_stat
        )

        ret = backend_repository.get_host_templates(self.HOST_UNDER_TEST)
        ret.sort(key=lambda x: x["tower_job_template_id"])

        assert len(ret) == 2
        expected = [
            {"tower_job_template_id": template_one.tower_job_template_id, "compliant": False, "successful": False},
            {"tower_job_template_id": template_two.tower_job_template_id, "compliant": True, "successful": True},
        ]
        actual = [
            {k: v for (k, v) in r.items() if k in ["compliant", "successful", "tower_job_template_id"]} for r in ret
        ]
        assert actual == expected
