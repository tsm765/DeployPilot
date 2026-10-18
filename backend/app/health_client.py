import os

import httpx


HEALTH_CHECK_TIMEOUT = 15.0
MAX_HEALTH_ERROR_CHARS = 2000


def get_runtime_health() -> dict:
    base_url = os.environ["DEMO_APP_BASE_URL"]

    health_url = f"{base_url.rstrip('/')}/health"

    try:
        response = httpx.get(
            health_url,
            timeout=HEALTH_CHECK_TIMEOUT,
        )

    except httpx.TimeoutException:
        return {
            "status": "unhealthy",
            "http_status": None,
            "url": health_url,
            "error": (
                "Runtime health check timed out "
                f"after {HEALTH_CHECK_TIMEOUT} seconds."
            ),
        }

    except httpx.RequestError as exc:
        return {
            "status": "unhealthy",
            "http_status": None,
            "url": health_url,
            "error": (
                "Runtime health check could not "
                f"reach the application: {exc}"
            ),
        }

    if response.status_code == 200:
        return {
            "status": "healthy",
            "http_status": 200,
            "url": health_url,
            "error": None,
        }

    error_text = response.text
    if len(error_text) > MAX_HEALTH_ERROR_CHARS:
        error_text = (
            error_text[:MAX_HEALTH_ERROR_CHARS]
            + "... [truncated]"
        )

    return {
        "status": "unhealthy",
        "http_status": response.status_code,
        "url": health_url,
        "error": error_text,
    }
