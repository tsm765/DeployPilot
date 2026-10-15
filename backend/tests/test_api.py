from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_root():
    response = client.get("/")

    assert response.status_code == 200
    assert response.json() == {
        "message": "DeployPilot backend is running"
    }


def test_health():
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {
        "status": "healthy"
    }


def test_deployment_status():
    response = client.get("/api/deployment")

    assert response.status_code == 200
    assert response.json() == {
        "application": "demo-api",
        "environment": "production",
        "build": "passed",
        "tests": "passed",
        "container": "passed",
        "deployment": "failed",
    }


def test_analyze_failure():
    payload = {
        "application": "demo-api",
        "environment": "production",
        "stage": "runtime",
        "error_message": "Required environment variable DEMO_CONFIG is missing",
        "logs": [
            "Health check returned HTTP 500"
        ],
        "health_status": "unhealthy",
    }

    response = client.post(
        "/api/analyze",
        json=payload,
    )

    assert response.status_code == 200
    assert response.json() == {
        "stage": "runtime",
        "problem": "Required environment variable DEMO_CONFIG is missing",
        "likely_cause": "Failure analysis is not connected to AI yet.",
        "suggested_fix": "Review the supplied error message and logs.",
    }


def test_analyze_failure_rejects_invalid_stage():
    payload = {
        "application": "demo-api",
        "environment": "production",
        "stage": "something-random",
        "error_message": "Example failure",
    }

    response = client.post(
        "/api/analyze",
        json=payload,
    )

    assert response.status_code == 422
