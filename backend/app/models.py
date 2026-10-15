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


class FailureEvidence(BaseModel):
    application: str
    environment: str
    stage: FailureStage
    error_message: str
    logs: list[str] = Field(default_factory=list)
    exit_code: int | None = None
    health_status: str | None = None


class FailureAnalysis(BaseModel):
    stage: FailureStage
    problem: str
    likely_cause: str
    suggested_fix: str
