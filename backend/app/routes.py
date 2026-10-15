from fastapi import APIRouter

from app.models import DeploymentStatus, FailureAnalysis, FailureEvidence

router = APIRouter()


@router.get("/api/deployment", response_model=DeploymentStatus)
def get_deployment_status():
    return DeploymentStatus(
        application="demo-api",
        environment="production",
        build="passed",
        tests="passed",
        container="passed",
        deployment="failed",
    )


@router.post("/api/analyze", response_model=FailureAnalysis)
def analyze_failure(failure: FailureEvidence):
    return FailureAnalysis(
        stage=failure.stage,
        problem=failure.error_message,
        likely_cause="Failure analysis is not connected to AI yet.",
        suggested_fix="Review the supplied error message and logs.",
    )
