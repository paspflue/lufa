from conftest import AUTH_PASS, AUTH_USER
from flask import Flask


def test_login(app: Flask):
    app_client = app.test_client()
    app_client.get("/logout")

    # test unauthorized
    jobs_unauthorized = app_client.get("/jobs")
    assert jobs_unauthorized.status_code == 302 and "/login?next=" in jobs_unauthorized.location

    # login
    app_client.post("/login?next=/jobs", data={"username": AUTH_USER, "password": AUTH_PASS})

    job_authorized = app_client.get("/jobs")
    assert job_authorized.status_code == 200

    # logout
    app_client.get("/logout")
    jobs_logout = app_client.get("/jobs")
    assert jobs_logout.status_code == 302 and "/login?next=" in jobs_logout.location


def test_redirect_login_on_invalid_next(app: Flask):
    app_client = app.test_client()
    redirect = app_client.post("/login?next=http://google.com/", data={"username": AUTH_USER, "password": AUTH_PASS})
    assert redirect.status_code == 302 and redirect.location == "/"


def test_redirect_login_on_valid_next(app: Flask):
    app_client = app.test_client()
    redirect = app_client.post("/login?next=/jobs", data={"username": AUTH_USER, "password": AUTH_PASS})
    assert redirect.status_code == 302 and redirect.location == "/jobs"
