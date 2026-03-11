import logging
from abc import ABC, abstractmethod
from typing import Optional

import requests

logger = logging.getLogger(__name__)


class AwxClient(ABC):
    @abstractmethod
    def get_template_organisation(self, job_template_id) -> Optional[str]:
        pass


# returns only None
# for tests only or if no token is defined
class NoneAwxClient(AwxClient):
    def get_template_organisation(self, job_template_id) -> Optional[str]:
        return None


class ApiAwxClient(AwxClient):
    def __init__(self, awx_base_url: str, awx_token: str, ssl_verify: bool = True):
        self.awx_base_url = awx_base_url
        self.awx_token = awx_token
        self.ssl_verify = ssl_verify

    def get_template_organisation(self, job_template_id) -> Optional[str]:
        url = f"{self.awx_base_url}/api/v2/job_templates/{job_template_id}"
        try:
            response = requests.get(
                url,
                headers={"Authorization": f"Bearer {self.awx_token}"},
                verify=self.ssl_verify,
            )
        except Exception as ex:
            logger.error("Error on connecting to AWX %s %s", url, ex)
        else:
            if response.status_code == 200:
                data = response.json()
                try:
                    return data["summary_fields"]["organization"]["name"]
                except KeyError:
                    pass
            else:
                logger.warning(
                    "AWX get_template_organisation is not 200: Status_code: %s; Payload: '%s'",
                    response.status_code,
                    response.content,
                )

        return None
