from lufa import drop_unsafe_redirects


def test_redirects_to_start_on_none():
    actual = drop_unsafe_redirects(None)

    assert actual is None


def test_does_not_redirect_to_external_sites():
    actual = drop_unsafe_redirects("https://www.google.com/")

    assert actual is None


def test_redirects_to_internal_pages():
    actual = drop_unsafe_redirects("/jobs")

    assert actual == "/jobs"
