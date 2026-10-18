import json
import logging
import os

from openai import OpenAI

from app.models import FailureEvidence
from app.redaction import (
    redact_lines,
    redact_text,
)

logger = logging.getLogger("deploypilot")


def analyze_failure_with_ai(
    failure: FailureEvidence,
) -> dict[str, str]:
    client = OpenAI(
        api_key=os.environ["OPENAI_API_KEY"]
    )
    model = os.getenv(
        "OPENAI_MODEL",
        "gpt-6-luna",
    )

    evidence = {
        "stage": failure.stage,
        "error_message": redact_text(
            failure.error_message
        ),
        "logs": redact_lines(
            failure.logs
        ),
        "exit_code": failure.exit_code,
        "health_status": failure.health_status,
        "http_status": failure.http_status,
    }

    logger.info(
        "AI failure analysis requested",
        extra={
            "event": "ai_analysis_requested",
            "stage": failure.stage,
        },
    )

    response = client.responses.create(
        model=model,
        store=False,
        instructions=(
            "You are the DeployPilot deployment failure assistant. "
            "Analyze only the supplied deployment evidence. "
            "Do not invent facts that are not supported by the evidence. "
            "Explain the problem concisely for a developer. "
            "If the exact cause cannot be proven, clearly describe it "
            "as the likely cause."
        ),
        input=(
            "Analyze this deployment failure evidence:\n\n"
            f"{json.dumps(evidence, indent=2)}"
        ),
        text={
            "format": {
                "type": "json_schema",
                "name": "deployment_failure_analysis",
                "strict": True,
                "schema": {
                    "type": "object",
                    "properties": {
                        "problem": {
                            "type": "string"
                        },
                        "likely_cause": {
                            "type": "string"
                        },
                        "suggested_fix": {
                            "type": "string"
                        },
                    },
                    "required": [
                        "problem",
                        "likely_cause",
                        "suggested_fix",
                    ],
                    "additionalProperties": False,
                },
            }
        },
        max_output_tokens=400,
    )

    analysis = json.loads(response.output_text)

    logger.info(
        "AI failure analysis completed",
        extra={
            "event": "ai_analysis_completed",
            "stage": failure.stage,
            "status": "passed",
        },
    )

    return analysis
