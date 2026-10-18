import os

import httpx


GITHUB_API_VERSION = "2026-03-10"
GITHUB_REQUEST_TIMEOUT = 15.0

STEP_STAGE_MAP = {
    "Run demo app tests": "tests",
    "Build demo app Docker image": "build",
    "Push demo app image to ACR": "container",
    "Deploy image to Azure Container Apps": "deployment",
}


def get_latest_workflow_run() -> dict:
    owner = os.environ["GITHUB_OWNER"]
    repository = os.getenv(
        "GITHUB_REPOSITORY",
        "deploypilot",
    )
    workflow = os.getenv(
        "GITHUB_WORKFLOW",
        "ci.yml",
    )
    url = (
        f"https://api.github.com/repos/"
        f"{owner}/{repository}/actions/workflows/"
        f"{workflow}/runs"
    )
    headers = {
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": GITHUB_API_VERSION,
    }
    token = os.getenv("GITHUB_TOKEN")
    if token:
        headers["Authorization"] = f"Bearer {token}"
    params = {
        "branch": "main",
        "event": "push",
        "per_page": 1,
    }
    response = httpx.get(
        url,
        headers=headers,
        params=params,
        timeout=GITHUB_REQUEST_TIMEOUT,
    )
    response.raise_for_status()
    workflow_runs = response.json()["workflow_runs"]
    if not workflow_runs:
        raise RuntimeError(
            "No GitHub Actions workflow runs found."
        )
    return workflow_runs[0]


def get_workflow_jobs(run_id: int) -> list[dict]:
    owner = os.environ["GITHUB_OWNER"]
    repository = os.getenv(
        "GITHUB_REPOSITORY",
        "deploypilot",
    )
    url = (
        f"https://api.github.com/repos/"
        f"{owner}/{repository}/actions/runs/"
        f"{run_id}/jobs"
    )
    headers = {
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": GITHUB_API_VERSION,
    }
    token = os.getenv("GITHUB_TOKEN")
    if token:
        headers["Authorization"] = f"Bearer {token}"
    params = {
        "filter": "latest",
        "per_page": 100,
    }
    response = httpx.get(
        url,
        headers=headers,
        params=params,
        timeout=GITHUB_REQUEST_TIMEOUT,
    )
    response.raise_for_status()
    return response.json()["jobs"]


def github_status_to_stage_status(
    status: str,
    conclusion: str | None,
) -> str:
    if status in {
        "queued",
        "pending",
        "waiting",
        "requested",
    }:
        return "pending"
    if status == "in_progress":
        return "running"
    if conclusion == "success":
        return "passed"
    if conclusion == "skipped":
        return "pending"
    return "failed"


def find_step(
    jobs: list[dict],
    step_name: str,
) -> dict | None:
    for job in jobs:
        for step in job.get("steps", []):
            if step.get("name") == step_name:
                return step
    return None


def get_step_stage_status(
    jobs: list[dict],
    step_name: str,
) -> str:
    step = find_step(
        jobs,
        step_name,
    )
    if step is None:
        return "pending"
    return github_status_to_stage_status(
        step["status"],
        step.get("conclusion"),
    )


def find_failed_pipeline_step(
    jobs: list[dict],
) -> tuple[dict, dict, str]:
    for job in jobs:
        for step in job.get("steps", []):
            step_name = step.get("name")
            if (
                step.get("conclusion") == "failure"
                and step_name in STEP_STAGE_MAP
            ):
                return (
                    job,
                    step,
                    STEP_STAGE_MAP[step_name],
                )
    raise RuntimeError(
        "No recognized failed pipeline step found."
    )


def get_job_logs(job_id: int) -> str:
    owner = os.environ["GITHUB_OWNER"]
    repository = os.getenv(
        "GITHUB_REPOSITORY",
        "deploypilot",
    )
    url = (
        f"https://api.github.com/repos/"
        f"{owner}/{repository}/actions/jobs/"
        f"{job_id}/logs"
    )
    headers = {
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": GITHUB_API_VERSION,
    }
    token = os.getenv("GITHUB_TOKEN")
    if token:
        headers["Authorization"] = f"Bearer {token}"
    response = httpx.get(
        url,
        headers=headers,
        timeout=GITHUB_REQUEST_TIMEOUT,
        follow_redirects=True,
    )
    response.raise_for_status()
    return response.text


def get_log_excerpt(
    log_text: str,
    max_lines: int = 60,
) -> list[str]:
    lines = [
        line.strip()
        for line in log_text.splitlines()
        if line.strip()
    ]
    return lines[-max_lines:]
