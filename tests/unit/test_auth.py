import json

import pytest
from flask import Flask
from flask.testing import FlaskClient

from lufa.auth import ro_token_required, token_required

TOKEN = "1234"
INVALID_TOKEN = "5678"
RO_TOKEN = "4321"


@pytest.fixture
def app() -> Flask:
    app = Flask(__name__)

    app.config.setdefault("API_KEYS", [TOKEN])

    @app.route("/hello", methods=["POST"])
    @token_required
    def hello():
        return "Hello", 200

    @app.route("/hello_ro", methods=["POST"])
    @ro_token_required
    def hello_ro():
        return "Hello", 200

    return app


@pytest.fixture
def client(app: Flask) -> FlaskClient:
    return app.test_client()


@pytest.fixture
def client_with_ro_token(app: Flask) -> FlaskClient:
    app.config.setdefault("API_KEYS_RO", [RO_TOKEN])
    return app.test_client()


def test_token_required(client: FlaskClient):
    # test without Authorization
    resp = client.post("/hello", data="{}")
    assert resp.status_code == 401

    # test with api_key in Data
    resp = client.post("/hello", data=json.dumps({"api_key": f"{INVALID_TOKEN}"}))
    assert resp.status_code == 401

    # test with token in Authorization header
    resp = client.post("/hello", data="{}", headers={"Authorization": f"token {INVALID_TOKEN}"})
    assert resp.status_code == 401

    # test with api_key in Data
    resp = client.post("/hello", data=json.dumps({"api_key": f"{TOKEN}"}))
    assert resp.status_code == 200

    # test with token in Authorization header
    resp = client.post("/hello", data="{}", headers={"Authorization": f"token {TOKEN}"})
    assert resp.status_code == 200


def test_rw_token_accepted_for_ro_token_required(client_with_ro_token: FlaskClient):
    client = client_with_ro_token
    # test without Authorization
    resp = client.post("/hello_ro", data="{}")
    assert resp.status_code == 401

    # test with api_key in Data
    resp = client.post("/hello_ro", data=json.dumps({"api_key": f"{INVALID_TOKEN}"}))
    assert resp.status_code == 401

    # test with token in Authorization header
    resp = client.post("/hello_ro", data="{}", headers={"Authorization": f"token {INVALID_TOKEN}"})
    assert resp.status_code == 401

    # test with api_key in Data
    resp = client.post("/hello_ro", data=json.dumps({"api_key": f"{TOKEN}"}))
    assert resp.status_code == 200

    # test with token in Authorization header
    resp = client.post("/hello_ro", data="{}", headers={"Authorization": f"token {TOKEN}"})
    assert resp.status_code == 200


def test_ro_token_not_accepted_for_token_required(client: FlaskClient):
    # test with api_key in Data
    resp = client.post("/hello", data=json.dumps({"api_key": f"{RO_TOKEN}"}))
    assert resp.status_code == 401

    # test with token in Authorization header
    resp = client.post("/hello", data="{}", headers={"Authorization": f"token {RO_TOKEN}"})
    assert resp.status_code == 401


def test_ro_token_accepted_for_ro_token_required(client_with_ro_token: FlaskClient):
    client = client_with_ro_token
    # test with api_key in Data
    resp = client.post("/hello_ro", data=json.dumps({"api_key": f"{RO_TOKEN}"}))
    assert resp.status_code == 200

    # test with token in Authorization header
    resp = client.post("/hello_ro", data="{}", headers={"Authorization": f"token {RO_TOKEN}"})
    assert resp.status_code == 200
