import json
from unittest.mock import patch

from lufa.awx import ApiAwxClient


class TestApiAwxClient:
    @patch("requests.get")
    def test_get_template_organisation(self, mock_get):
        # test successful response with mocket json return
        with open("./test_data/awx_job_templates_data.json") as json_data:
            mock_response = mock_get.return_value
            mock_response.status_code = 200
            mock_response.json.return_value = json.load(json_data)

            client = ApiAwxClient("https://awx.example.com", "1234")
            org = client.get_template_organisation(123)
            assert org == "Sample"

        # test with status_code != 200
        mock_response = mock_get.return_value
        mock_response.status_code = 400
        mock_response.json.return_value = {}
        client = ApiAwxClient("https://awx.example.com", "1234")
        assert client.get_template_organisation(123) is None

        # test with wrong json return (key error)
        mock_response = mock_get.return_value
        mock_response.status_code = 200
        mock_response.json.return_value = {}
        client = ApiAwxClient("https://awx.example.com", "1234")
        assert client.get_template_organisation(123) is None
