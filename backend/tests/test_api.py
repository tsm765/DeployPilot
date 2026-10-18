from fastapi.testclient import TestClient

from app.main import app
from app.models import FailureEvidence

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


def test_deployment_status_from_github(
    monkeypatch,
):
    fake_run = {
        "id": 123456789,
        "run_number": 57,
        "head_branch": "main",
        "head_sha": "abc123456789",
        "html_url": (
            "https://github.com/example/"
            "deploypilot/actions/runs/123456789"
        ),
        "created_at": "2026-10-17T20:00:00Z",
        "updated_at": "2026-10-17T20:02:00Z",
    }

    fake_jobs = [
        {
            "steps": [
                {
                    "name": "Run demo app tests",
                    "status": "completed",
                    "conclusion": "success",
                },
                {
                    "name": "Build demo app Docker image",
                    "status": "completed",
                    "conclusion": "success",
                },
            ]
        },
        {
            "steps": [
                {
                    "name": "Push demo app image to ACR",
                    "status": "completed",
                    "conclusion": "success",
                },
                {
                    "name": (
                        "Deploy image to "
                        "Azure Container Apps"
                    ),
                    "status": "completed",
                    "conclusion": "success",
                },
            ]
        },
    ]

    monkeypatch.setattr(
        "app.routes.get_latest_workflow_run",
        lambda: fake_run,
    )

    monkeypatch.setattr(
        "app.routes.get_workflow_jobs",
        lambda run_id: fake_jobs,
    )

    monkeypatch.setattr(
        "app.routes.get_runtime_health",
        lambda: {
            "status": "healthy",
            "http_status": 200,
            "url": "https://example.test/health",
            "error": None,
        },
    )

    response = client.get(
        "/api/deployment"
    )

    assert response.status_code == 200

    data = response.json()

    assert data["tests"] == "passed"
    assert data["build"] == "passed"
    assert data["container"] == "passed"
    assert data["deployment"] == "passed"
    assert data["runtime"] == "passed"

    assert data["run_id"] == 123456789
    assert data["run_number"] == 57
    assert data["branch"] == "main"
    assert data["commit_sha"] == "abc123456789"


def test_deployment_status_runtime_failed(
    monkeypatch,
):
    fake_run = {
        "id": 123456789,
        "run_number": 57,
        "head_branch": "main",
        "head_sha": "abc123456789",
        "html_url": (
            "https://github.com/example/"
            "deploypilot/actions/runs/123456789"
        ),
        "created_at": "2026-10-17T20:00:00Z",
        "updated_at": "2026-10-17T20:02:00Z",
    }

    fake_jobs = [
        {
            "steps": [
                {
                    "name": "Run demo app tests",
                    "status": "completed",
                    "conclusion": "success",
                },
                {
                    "name": "Build demo app Docker image",
                    "status": "completed",
                    "conclusion": "success",
                },
                {
                    "name": "Push demo app image to ACR",
                    "status": "completed",
                    "conclusion": "success",
                },
                {
                    "name": (
                        "Deploy image to "
                        "Azure Container Apps"
                    ),
                    "status": "completed",
                    "conclusion": "success",
                },
            ]
        }
    ]

    monkeypatch.setattr(
        "app.routes.get_latest_workflow_run",
        lambda: fake_run,
    )

    monkeypatch.setattr(
        "app.routes.get_workflow_jobs",
        lambda run_id: fake_jobs,
    )

    monkeypatch.setattr(
        "app.routes.get_runtime_health",
        lambda: {
            "status": "unhealthy",
            "http_status": 500,
            "url": "https://example.test/health",
            "error": (
                '{"detail":"DEMO_CONFIG missing"}'
            ),
        },
    )

    response = client.get(
        "/api/deployment"
    )

    assert response.status_code == 200

    data = response.json()

    assert data["tests"] == "passed"
    assert data["build"] == "passed"
    assert data["container"] == "passed"
    assert data["deployment"] == "passed"
    assert data["runtime"] == "failed"


def test_runtime_failure_evidence(
    monkeypatch,
):
    monkeypatch.setattr(
        "app.routes.get_runtime_health",
        lambda: {
            "status": "unhealthy",
            "http_status": 500,
            "url": "https://example.test/health",
            "error": (
                '{"detail":"Required environment '
                'variable DEMO_CONFIG is missing"}'
            ),
        },
    )

    response = client.get(
        "/api/runtime-failure-evidence"
    )

    assert response.status_code == 200

    data = response.json()

    assert data["stage"] == "runtime"
    assert data["health_status"] == "unhealthy"
    assert data["http_status"] == 500

    assert (
        "HTTP 500"
        in data["error_message"]
    )

    assert any(
        "DEMO_CONFIG" in line
        for line in data["logs"]
    )


def test_runtime_failure_evidence_when_healthy(
    monkeypatch,
):
    monkeypatch.setattr(
        "app.routes.get_runtime_health",
        lambda: {
            "status": "healthy",
            "http_status": 200,
            "url": "https://example.test/health",
            "error": None,
        },
    )

    response = client.get(
        "/api/runtime-failure-evidence"
    )

    assert response.status_code == 404


def test_runtime_failure_evidence_returns_consistent_error(
    monkeypatch,
):
    monkeypatch.setattr(
        "app.routes.get_runtime_health",
        lambda: {
            "status": "healthy",
            "http_status": 200,
            "url": "https://example.test/health",
            "error": None,
        },
    )

    response = client.get(
        "/api/runtime-failure-evidence"
    )

    assert response.status_code == 404
    assert response.json() == {
        "error": {
            "code": "no_failure_evidence",
            "message": (
                "Runtime is healthy; "
                "no runtime failure evidence available."
            ),
        }
    }


def test_runtime_failure_report(
    monkeypatch,
):
    fake_failure = FailureEvidence(
        application="demo-api",
        environment="production",
        stage="runtime",
        error_message=(
            "Runtime health check "
            "returned HTTP 500."
        ),
        logs=[
            "HTTP status: 500",
            (
                "Health response/error: "
                "DEMO_CONFIG is missing"
            ),
        ],
        health_status="unhealthy",
        http_status=500,
    )

    monkeypatch.setattr(
        "app.routes.collect_runtime_failure_evidence",
        lambda: fake_failure,
    )

    monkeypatch.setattr(
        "app.routes.analyze_failure_with_ai",
        lambda failure: {
            "problem": (
                "The application health "
                "check is failing."
            ),
            "likely_cause": (
                "DEMO_CONFIG is missing."
            ),
            "suggested_fix": (
                "Configure DEMO_CONFIG."
            ),
        },
    )

    response = client.post(
        "/api/runtime-failure-report"
    )

    assert response.status_code == 200

    data = response.json()

    assert (
        data["evidence"]["stage"]
        == "runtime"
    )

    assert (
        data["analysis"]["stage"]
        == "runtime"
    )

    assert (
        data["evidence"]["http_status"]
        == 500
    )

    assert (
        data["analysis"]["likely_cause"]
        == "DEMO_CONFIG is missing."
    )


def test_failure_report_uses_exact_run(
    monkeypatch,
):
    fake_failure = FailureEvidence(
        application="demo-api",
        environment="production",
        stage="tests",
        error_message=(
            "GitHub Actions step failed: "
            "Run demo app tests"
        ),
        logs=[
            "AssertionError",
            "1 failed, 1 passed",
        ],
    )

    def fake_collect_failure_evidence(
        run_id: int,
    ):
        assert run_id == 987654321
        return fake_failure

    monkeypatch.setattr(
        "app.routes.collect_failure_evidence",
        fake_collect_failure_evidence,
    )

    monkeypatch.setattr(
        "app.routes.analyze_failure_with_ai",
        lambda failure: {
            "problem": "A unit test failed.",
            "likely_cause": (
                "The expected response did not "
                "match the actual response."
            ),
            "suggested_fix": (
                "Correct the test expectation."
            ),
        },
    )

    response = client.post(
        "/api/failure-report/987654321"
    )

    assert response.status_code == 200

    data = response.json()

    assert data["run_id"] == 987654321

    assert (
        data["evidence"]["stage"]
        == "tests"
    )

    assert (
        data["analysis"]["stage"]
        == "tests"
    )

    assert (
        data["analysis"]["problem"]
        == "A unit test failed."
    )


def test_analyze_failure(
    monkeypatch,
):
    monkeypatch.setattr(
        "app.routes.analyze_failure_with_ai",
        lambda failure: {
            "problem": "Test problem",
            "likely_cause": "Test cause",
            "suggested_fix": "Test fix",
        },
    )

    response = client.post(
        "/api/analyze",
        json={
            "application": "demo-api",
            "environment": "production",
            "stage": "tests",
            "error_message": "pytest failed",
            "logs": [
                "AssertionError"
            ],
        },
    )

    assert response.status_code == 200
    assert response.json() == {
        "stage": "tests",
        "problem": "Test problem",
        "likely_cause": "Test cause",
        "suggested_fix": "Test fix",
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


def test_unknown_endpoint_uses_consistent_error_shape():
    response = client.get(
        "/api/does-not-exist"
    )

    assert response.status_code == 404
    data = response.json()
    assert data["error"]["code"] == "http_404"
    assert "message" in data["error"]


def test_invalid_request_uses_consistent_error_shape():
    response = client.post(
        "/api/analyze",
        json={},
    )

    assert response.status_code == 422
    assert response.json() == {
        "error": {
            "code": "validation_error",
            "message": "Request validation failed.",
        }
    }
