import logging

from fastapi import APIRouter
import httpx
from openai import OpenAIError

from app.ai_client import analyze_failure_with_ai
from app.errors import APIError
from app.github_client import (
    find_failed_pipeline_step,
    get_job_logs,
    get_latest_workflow_run,
    get_log_excerpt,
    get_step_stage_status,
    get_workflow_jobs,
)
from app.health_client import get_runtime_health
from app.models import (
    DeploymentStatus,
    FailureAnalysis,
    FailureEvidence,
    FailureReport,
    GitHubWorkflowRun,
    RuntimeFailureReport,
    RuntimeHealth,
)
from app.redaction import (
    redact_lines,
    redact_text,
)

logger = logging.getLogger("deploypilot")
router = APIRouter()


@router.get(
    "/api/runtime-health",
    response_model=RuntimeHealth,
)
def get_application_runtime_health():
    try:
        return RuntimeHealth(
            **get_runtime_health()
        )
    except KeyError:
        raise APIError(
            status_code=500,
            code="configuration_error",
            message="DEMO_APP_BASE_URL is not configured.",
        )


def collect_failure_evidence(
    run_id: int,
) -> FailureEvidence:
    jobs = get_workflow_jobs(
        run_id
    )
    job, step, stage = (
        find_failed_pipeline_step(jobs)
    )
    log_text = get_job_logs(
        job["id"]
    )
    logs = redact_lines(
        get_log_excerpt(
            log_text
        )
    )
    logger.info(
        "Pipeline failure evidence collected",
        extra={
            "event": "pipeline_failure_evidence",
            "run_id": run_id,
            "stage": stage,
            "status": "failed",
        },
    )
    return FailureEvidence(
        application="demo-api",
        environment="production",
        stage=stage,
        error_message=(
            f"GitHub Actions step failed: "
            f"{step['name']}"
        ),
        logs=logs,
    )


def collect_runtime_failure_evidence() -> FailureEvidence:
    health = get_runtime_health()

    if health["status"] == "healthy":
        raise RuntimeError(
            "Runtime is healthy; no runtime failure evidence available."
        )

    http_status = health["http_status"]

    logger.warning(
        "Runtime health check failed",
        extra={
            "event": "runtime_failure",
            "stage": "runtime",
            "status": "failed",
            "http_status": http_status,
        },
    )

    if http_status is None:
        error_message = (
            "Runtime health check could not reach the application."
        )
    else:
        error_message = (
            f"Runtime health check returned HTTP {http_status}."
        )

    logs = [
        redact_text(
            f"Health URL: {health['url']}"
        ),
    ]

    if http_status is not None:
        logs.append(
            f"HTTP status: {http_status}"
        )

    if health["error"]:
        logs.append(
            redact_text(
                "Health response/error: "
                f"{health['error']}"
            )
        )

    return FailureEvidence(
        application="demo-api",
        environment="production",
        stage="runtime",
        error_message=error_message,
        logs=logs,
        health_status="unhealthy",
        http_status=http_status,
    )


@router.get(
    "/api/runtime-failure-evidence",
    response_model=FailureEvidence,
)
def get_runtime_failure_evidence():
    try:
        return collect_runtime_failure_evidence()
    except KeyError:
        raise APIError(
            status_code=500,
            code="configuration_error",
            message="DEMO_APP_BASE_URL is not configured.",
        )
    except RuntimeError as exc:
        raise APIError(
            status_code=404,
            code="no_failure_evidence",
            message=str(exc),
        )


@router.post(
    "/api/runtime-failure-report",
    response_model=RuntimeFailureReport,
)
def get_runtime_failure_report():
    try:
        failure = collect_runtime_failure_evidence()

        analysis_data = analyze_failure_with_ai(
            failure
        )

    except KeyError:
        raise APIError(
            status_code=500,
            code="configuration_error",
            message="Required server configuration is missing.",
        )

    except RuntimeError as exc:
        raise APIError(
            status_code=404,
            code="no_failure_evidence",
            message=str(exc),
        )

    except OpenAIError:
        logger.exception(
            "AI service request failed",
            extra={
                "event": "ai_service_error",
                "status": "failed",
            },
        )
        raise APIError(
            status_code=502,
            code="ai_service_error",
            message=(
                "Failure analysis could not be generated "
                "because the AI service request failed."
            ),
        )

    analysis = FailureAnalysis(
        stage=failure.stage,
        problem=analysis_data["problem"],
        likely_cause=analysis_data["likely_cause"],
        suggested_fix=analysis_data["suggested_fix"],
    )

    return RuntimeFailureReport(
        evidence=failure,
        analysis=analysis,
    )


@router.get(
    "/api/deployment",
    response_model=DeploymentStatus,
)
def get_deployment_status():
    try:
        run = get_latest_workflow_run()
        jobs = get_workflow_jobs(run["id"])
    except KeyError:
        raise APIError(
            status_code=500,
            code="configuration_error",
            message="GITHUB_OWNER is not configured.",
        )
    except httpx.HTTPError:
        logger.exception(
            "GitHub API request failed",
            extra={
                "event": "github_api_error",
                "status": "failed",
            },
        )
        raise APIError(
            status_code=502,
            code="github_api_error",
            message="GitHub API request failed.",
        )
    except RuntimeError as exc:
        raise APIError(
            status_code=404,
            code="workflow_not_found",
            message=str(exc),
        )

    try:
        runtime_health = get_runtime_health()
    except KeyError:
        raise APIError(
            status_code=500,
            code="configuration_error",
            message="DEMO_APP_BASE_URL is not configured.",
        )
    runtime_status = (
        "passed"
        if runtime_health["status"] == "healthy"
        else "failed"
    )

    deployment = DeploymentStatus(
        application="demo-api",
        environment="production",
        tests=get_step_stage_status(
            jobs,
            "Run demo app tests",
        ),
        build=get_step_stage_status(
            jobs,
            "Build demo app Docker image",
        ),
        container=get_step_stage_status(
            jobs,
            "Push demo app image to ACR",
        ),
        deployment=get_step_stage_status(
            jobs,
            "Deploy image to Azure Container Apps",
        ),
        runtime=runtime_status,
        run_id=run["id"],
        run_number=run["run_number"],
        branch=run["head_branch"],
        commit_sha=run["head_sha"],
        workflow_url=run["html_url"],
        created_at=run["created_at"],
        updated_at=run["updated_at"],
    )

    logger.info(
        "Deployment status collected",
        extra={
            "event": "deployment_status",
            "run_id": run["id"],
            "status": (
                "failed"
                if "failed" in {
                    deployment.tests,
                    deployment.build,
                    deployment.container,
                    deployment.deployment,
                    deployment.runtime,
                }
                else "passed"
            ),
        },
    )

    return deployment


@router.get(
    "/api/failure-evidence/{run_id}",
    response_model=FailureEvidence,
)
def get_failure_evidence(
    run_id: int,
):
    try:
        return collect_failure_evidence(
            run_id
        )
    except KeyError:
        raise APIError(
            status_code=500,
            code="configuration_error",
            message="Required server configuration is missing.",
        )
    except httpx.HTTPError:
        logger.exception(
            "GitHub API request failed",
            extra={
                "event": "github_api_error",
                "run_id": run_id,
                "status": "failed",
            },
        )
        raise APIError(
            status_code=502,
            code="github_api_error",
            message="GitHub API request failed.",
        )
    except RuntimeError as exc:
        raise APIError(
            status_code=404,
            code="no_failure_evidence",
            message=str(exc),
        )


@router.post(
    "/api/analyze",
    response_model=FailureAnalysis,
)
def analyze_failure(
    failure: FailureEvidence,
):
    try:
        analysis = analyze_failure_with_ai(
            failure
        )
    except OpenAIError:
        logger.exception(
            "AI service request failed",
            extra={
                "event": "ai_service_error",
                "stage": failure.stage,
                "status": "failed",
            },
        )
        raise APIError(
            status_code=502,
            code="ai_service_error",
            message=(
                "Failure analysis could not be generated "
                "because the AI service request failed."
            ),
        )
    return FailureAnalysis(
        stage=failure.stage,
        problem=analysis["problem"],
        likely_cause=analysis["likely_cause"],
        suggested_fix=analysis["suggested_fix"],
    )


@router.post(
    "/api/failure-report/{run_id}",
    response_model=FailureReport,
)
def get_failure_report(
    run_id: int,
):
    try:
        failure = collect_failure_evidence(
            run_id
        )
        analysis_data = analyze_failure_with_ai(
            failure
        )
    except KeyError:
        raise APIError(
            status_code=500,
            code="configuration_error",
            message="Required server configuration is missing.",
        )
    except httpx.HTTPError:
        logger.exception(
            "GitHub API request failed",
            extra={
                "event": "github_api_error",
                "run_id": run_id,
                "status": "failed",
            },
        )
        raise APIError(
            status_code=502,
            code="github_api_error",
            message="GitHub API request failed.",
        )
    except RuntimeError as exc:
        raise APIError(
            status_code=404,
            code="no_failure_evidence",
            message=str(exc),
        )
    except OpenAIError:
        logger.exception(
            "AI service request failed",
            extra={
                "event": "ai_service_error",
                "run_id": run_id,
                "status": "failed",
            },
        )
        raise APIError(
            status_code=502,
            code="ai_service_error",
            message=(
                "Failure analysis could not be generated "
                "because the AI service request failed."
            ),
        )
    analysis = FailureAnalysis(
        stage=failure.stage,
        problem=analysis_data["problem"],
        likely_cause=analysis_data["likely_cause"],
        suggested_fix=analysis_data["suggested_fix"],
    )
    return FailureReport(
        run_id=run_id,
        evidence=failure,
        analysis=analysis,
    )


@router.get(
    "/api/github/latest-run",
    response_model=GitHubWorkflowRun,
)
def get_latest_github_run():
    try:
        run = get_latest_workflow_run()
    except KeyError:
        raise APIError(
            status_code=500,
            code="configuration_error",
            message="GITHUB_OWNER is not configured.",
        )
    except httpx.HTTPError:
        logger.exception(
            "GitHub API request failed",
            extra={
                "event": "github_api_error",
                "status": "failed",
            },
        )
        raise APIError(
            status_code=502,
            code="github_api_error",
            message="GitHub API request failed.",
        )
    except RuntimeError as exc:
        raise APIError(
            status_code=404,
            code="workflow_not_found",
            message=str(exc),
        )
    return GitHubWorkflowRun(
        run_id=run["id"],
        status=run["status"],
        conclusion=run["conclusion"],
        branch=run["head_branch"],
        commit_sha=run["head_sha"],
        workflow_url=run["html_url"],
        created_at=run["created_at"],
        updated_at=run["updated_at"],
    )
