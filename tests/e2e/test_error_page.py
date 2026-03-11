from flask.testing import FlaskClient

# non-existent ids
TEST_ENDPOINTS = [
    "/jobs/778989",
    "/workflows/778989",
    "/templates/778989",
]


def test_404_resource_not_found(client: FlaskClient):
    for endpoint in TEST_ENDPOINTS:
        response = client.get(endpoint)

        assert response.status_code == 404
        assert b"Resource not found" in response.data or b"Error" in response.data
