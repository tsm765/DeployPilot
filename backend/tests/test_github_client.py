import httpx
import pytest

from app.github_client import (
    find_failed_pipeline_step,
    get_step_stage_status,
    get_workflow_jobs,
    github_status_to_stage_status,
)


@pytest.mark.parametrize(
    ("status", "conclusion", "expected"),
    [
        ("queued", None, "pending"),
        ("pending", None, "pending"),
        ("in_progress", None, "running"),
        ("completed", "success", "passed"),
        ("completed", "failure", "failed"),
        ("completed", "cancelled", "failed"),
        ("completed", "skipped", "pending"),
    ],
)
def test_github_status_to_stage_status(
    status,
    conclusion,
    expected,
):
    assert (
        github_status_to_stage_status(
            status,
            conclusion,
        )
        == expected
    )


def test_get_step_stage_status():
    jobs = [
        {
            "steps": [
                {
                    "name": "Run demo app tests",
                    "status": "completed",
                    "conclusion": "success",
                }
            ]
        }
    ]

    assert (
        get_step_stage_status(
            jobs,
            "Run demo app tests",
        )
        == "passed"
    )


def test_missing_step_is_pending():
    jobs = []

    assert (
        get_step_stage_status(
            jobs,
            "Build demo app Docker image",
        )
        == "pending"
    )


def test_find_failed_pipeline_step():
    jobs = [
        {
            "id": 123,
            "name": "demo-app-ci",
            "steps": [
                {
                    "name": "Run demo app tests",
                    "status": "completed",
                    "conclusion": "failure",
                }
            ],
        }
    ]

    job, step, stage = (
        find_failed_pipeline_step(jobs)
    )

    assert job["id"] == 123
    assert step["name"] == "Run demo app tests"
    assert stage == "tests"


def test_github_timeout_is_not_treated_as_success(
    monkeypatch,
):
    monkeypatch.setenv(
        "GITHUB_OWNER",
        "example",
    )

    def fake_get(*args, **kwargs):
        request = httpx.Request(
            "GET",
            "https://api.github.com",
        )

        raise httpx.ReadTimeout(
            "Timed out",
            request=request,
        )

    monkeypatch.setattr(
        "app.github_client.httpx.get",
        fake_get,
    )

    with pytest.raises(
        httpx.ReadTimeout
    ):
        get_workflow_jobs(123)
