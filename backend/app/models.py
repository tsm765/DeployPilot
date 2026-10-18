from typing import Literal

from pydantic import BaseModel, Field

StageStatus = Literal[
    "pending",
    "running",
    "passed",
    "failed",
]

FailureStage = Literal[
    "tests",
    "build",
    "container",
    "deployment",
    "runtime",
]


class DeploymentStatus(BaseModel):
    application: str
    environment: str
    build: StageStatus
    tests: StageStatus
    container: StageStatus
    deployment: StageStatus
    runtime: StageStatus
    run_id: int
    run_number: int
    branch: str
    commit_sha: str
    workflow_url: str
    created_at: str
    updated_at: str


class FailureEvidence(BaseModel):
    application: str
    environment: str
    stage: FailureStage
    error_message: str
    logs: list[str] = Field(default_factory=list)
    exit_code: int | None = None
    health_status: str | None = None
    http_status: int | None = None


class FailureAnalysis(BaseModel):
    stage: FailureStage
    problem: str
    likely_cause: str
    suggested_fix: str


class GitHubWorkflowRun(BaseModel):
    run_id: int
    status: str
    conclusion: str | None
    branch: str
    commit_sha: str
    workflow_url: str
    created_at: str
    updated_at: str


class FailureReport(BaseModel):
    run_id: int
    evidence: FailureEvidence
    analysis: FailureAnalysis


class RuntimeFailureReport(BaseModel):
    evidence: FailureEvidence
    analysis: FailureAnalysis


class RuntimeHealth(BaseModel):
    status: Literal[
        "healthy",
        "unhealthy",
    ]
    http_status: int | None
    url: str
    error: str | None
