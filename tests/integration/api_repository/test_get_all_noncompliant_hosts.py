from __future__ import annotations

from datetime import timedelta

from lufa.repository.api_repository import ApiRepository
from tests.integration.conftest import HostIntependantTowerJobStats, LufaFactory


class TestGetAllNoncompliantHosts:
    HOST_UNDER_TEST = "HostUnderTest"

    def test_empty_repository(self, api_repository: ApiRepository):
        ret = api_repository.get_all_noncompliant_hosts()
        assert len(ret) == 0

    def test_compliant_with_all_tower_templates_have_compliance_interval_zero(
        self,
        api_repository: ApiRepository,
        lufa_factory: LufaFactory,
        any_stat: HostIntependantTowerJobStats,
    ):
        lufa_factory.add_tower_template().add_job_with_compliance_interval(0).with_stats(self.HOST_UNDER_TEST, any_stat)

        ret = api_repository.get_all_noncompliant_hosts()

        assert len(ret) == 0

    def test_non_compliant_with_only_failed_runs_and_positive_compliance_interval(
        self,
        api_repository: ApiRepository,
        lufa_factory: LufaFactory,
        failed_stat: HostIntependantTowerJobStats,
    ):
        lufa_factory.add_tower_template().add_job_with_compliance_interval(3).with_stats(
            self.HOST_UNDER_TEST, failed_stat
        )

        ret = api_repository.get_all_noncompliant_hosts()

        assert len(ret) == 1
        assert self.HOST_UNDER_TEST in ret
        assert ret[self.HOST_UNDER_TEST][0]["last_successful"] == 0

    def test_successful_run_within_positive_compliance_interval_is_compliant(
        self,
        api_repository: ApiRepository,
        lufa_factory: LufaFactory,
        success_stat: HostIntependantTowerJobStats,
    ):
        lufa_factory.add_tower_template().add_job_with_compliance_interval(3).with_stats(
            self.HOST_UNDER_TEST, success_stat
        )

        ret = api_repository.get_all_noncompliant_hosts()

        assert len(ret) == 0

    def test_successful_run_outside_positive_compliance_interval_is_non_compliant(
        self,
        api_repository: ApiRepository,
        lufa_factory: LufaFactory,
        success_stat: HostIntependantTowerJobStats,
    ):
        lufa_factory.add_tower_template().add_job_with_compliance_interval(3, started_ago=timedelta(days=4)).with_stats(
            self.HOST_UNDER_TEST, success_stat
        )

        ret = api_repository.get_all_noncompliant_hosts()

        assert len(ret) == 1
        assert self.HOST_UNDER_TEST in ret
        assert ret[self.HOST_UNDER_TEST][0]["last_successful"] > 1768849999

    def test_only_failed_runs_within_positive_compliance_interval_is_noncompliant(
        self,
        api_repository: ApiRepository,
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

        ret = api_repository.get_all_noncompliant_hosts()

        assert len(ret) == 1
        assert self.HOST_UNDER_TEST in ret
        assert ret[self.HOST_UNDER_TEST][0]["last_successful"] > 1768849999

    def test_mixture_of_failed_and_successful_runs_within_positive_compliance_interval_is_compliant(
        self,
        api_repository: ApiRepository,
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

        ret = api_repository.get_all_noncompliant_hosts()

        assert len(ret) == 0

    def test_mixture_of_failed_and_successful_runs_within_positive_compliance_interval_is_compliant_before(
        self,
        api_repository: ApiRepository,
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

        ret = api_repository.get_all_noncompliant_hosts()

        assert len(ret) == 0

    def test_mixture_of_failed_and_successful_runs_within_positive_compliance_interval_is_compliant_after(
        self,
        api_repository: ApiRepository,
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

        ret = api_repository.get_all_noncompliant_hosts()

        assert len(ret) == 0

    def test_compliant_host_does_not_affect_noncompliant_host(
        self,
        api_repository: ApiRepository,
        lufa_factory: LufaFactory,
        success_stat: HostIntependantTowerJobStats,
        failed_stat: HostIntependantTowerJobStats,
    ):
        other_host = "OtherHost"
        template = lufa_factory.add_tower_template()
        job = template.add_job_with_compliance_interval(3, started_ago=timedelta(days=2)).with_stats(
            self.HOST_UNDER_TEST, failed_stat
        )
        template.add_job_with_compliance_interval(3, started_ago=timedelta(days=2)).with_stats(other_host, success_stat)

        ret = api_repository.get_all_noncompliant_hosts()

        expected = {
            self.HOST_UNDER_TEST: [
                {
                    "last_successful": 0,
                    "last_job_run": job.tower_job_id,
                    "template_name": template.tower_job_template_name,
                    "tower_job_template_id": template.tower_job_template_id,
                    "compliance_interval_in_days": 3,
                    "playbook": template.playbook_path,
                    "organisation": template.awx_organisation,
                }
            ]
        }

        assert ret == expected

    def test_only_list_non_compliant_job_templates(
        self,
        api_repository: ApiRepository,
        lufa_factory: LufaFactory,
        any_stat: HostIntependantTowerJobStats,
        failed_stat: HostIntependantTowerJobStats,
    ):
        template_one = lufa_factory.add_tower_template()
        template_two = lufa_factory.add_tower_template()
        job_one = template_one.add_job_with_compliance_interval(3, started_ago=timedelta(days=2)).with_stats(
            self.HOST_UNDER_TEST, failed_stat
        )
        template_two.add_job_with_compliance_interval(3, started_ago=timedelta(days=2)).with_stats(
            self.HOST_UNDER_TEST, any_stat
        )

        ret = api_repository.get_all_noncompliant_hosts()

        assert ret == {
            self.HOST_UNDER_TEST: [
                {
                    "last_successful": 0,
                    "last_job_run": job_one.tower_job_id,
                    "compliance_interval_in_days": 3,
                    "playbook": template_one.playbook_path,
                    "template_name": template_one.tower_job_template_name,
                    "tower_job_template_id": template_one.tower_job_template_id,
                    "organisation": template_one.awx_organisation,
                }
            ]
        }
