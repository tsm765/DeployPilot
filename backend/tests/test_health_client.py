import httpx

from app.health_client import get_runtime_health


def test_runtime_health_healthy(
    monkeypatch,
):
    monkeypatch.setenv(
        "DEMO_APP_BASE_URL",
        "https://example.test",
    )

    def fake_get(
        url,
        timeout,
    ):
        return httpx.Response(
            status_code=200,
            text='{"status":"healthy"}',
        )

    monkeypatch.setattr(
        "app.health_client.httpx.get",
        fake_get,
    )

    result = get_runtime_health()

    assert result["status"] == "healthy"
    assert result["http_status"] == 200
    assert result["error"] is None
    assert (
        result["url"]
        == "https://example.test/health"
    )


def test_runtime_health_http_500(
    monkeypatch,
):
    monkeypatch.setenv(
        "DEMO_APP_BASE_URL",
        "https://example.test",
    )

    def fake_get(
        url,
        timeout,
    ):
        return httpx.Response(
            status_code=500,
            text=(
                '{"detail":"Required environment '
                'variable DEMO_CONFIG is missing"}'
            ),
        )

    monkeypatch.setattr(
        "app.health_client.httpx.get",
        fake_get,
    )

    result = get_runtime_health()

    assert result["status"] == "unhealthy"
    assert result["http_status"] == 500

    assert "DEMO_CONFIG" in result["error"]


def test_runtime_health_unreachable(
    monkeypatch,
):
    monkeypatch.setenv(
        "DEMO_APP_BASE_URL",
        "https://example.test",
    )

    def fake_get(
        url,
        timeout,
    ):
        request = httpx.Request(
            "GET",
            url,
        )

        raise httpx.ConnectError(
            "Connection failed",
            request=request,
        )

    monkeypatch.setattr(
        "app.health_client.httpx.get",
        fake_get,
    )

    result = get_runtime_health()

    assert result["status"] == "unhealthy"
    assert result["http_status"] is None

    assert (
        "could not reach"
        in result["error"]
    )


def test_runtime_health_timeout(
    monkeypatch,
):
    monkeypatch.setenv(
        "DEMO_APP_BASE_URL",
        "https://example.test",
    )

    def fake_get(
        url,
        timeout,
    ):
        request = httpx.Request(
            "GET",
            url,
        )

        raise httpx.ReadTimeout(
            "Timed out",
            request=request,
        )

    monkeypatch.setattr(
        "app.health_client.httpx.get",
        fake_get,
    )

    result = get_runtime_health()

    assert result["status"] == "unhealthy"
    assert result["http_status"] is None

    assert "timed out" in result["error"]


def test_runtime_health_truncates_large_error(
    monkeypatch,
):
    monkeypatch.setenv(
        "DEMO_APP_BASE_URL",
        "https://example.test",
    )

    large_error = "x" * 5000

    def fake_get(
        url,
        timeout,
    ):
        return httpx.Response(
            status_code=500,
            text=large_error,
        )

    monkeypatch.setattr(
        "app.health_client.httpx.get",
        fake_get,
    )

    result = get_runtime_health()

    assert result["status"] == "unhealthy"
    assert result["http_status"] == 500
    assert len(result["error"]) < 5000
    assert "[truncated]" in result["error"]
