import os
import re


REDACTED = "[REDACTED]"


SECRET_PATTERNS = [
    # GitHub tokens
    re.compile(
        r"\bgithub_pat_[A-Za-z0-9_]{20,}\b"
    ),
    re.compile(
        r"\bgh[pousr]_[A-Za-z0-9_]{20,}\b"
    ),

    # OpenAI-style API keys
    re.compile(
        r"\bsk-[A-Za-z0-9_-]{20,}\b"
    ),

    # Authorization headers
    re.compile(
        r"(?i)(authorization\s*:\s*(?:bearer|token)\s+)"
        r"[^\s]+"
    ),

    # Common key=value / key: value secrets
    re.compile(
        r"(?i)"
        r"((?:api[_-]?key|access[_-]?token|token|password|secret)"
        r"\s*[=:]\s*)"
        r"[^\s,;]+"
    ),

    # Sensitive URL query parameters
    re.compile(
        r"(?i)"
        r"([?&](?:access_token|token|api_key|sig|signature)=)"
        r"[^&\s]+"
    ),
]


def redact_text(text: str | None) -> str | None:
    if text is None:
        return None

    redacted = text

    # First remove exact secrets known to this process.
    for variable_name in (
        "GITHUB_TOKEN",
        "OPENAI_API_KEY",
    ):
        value = os.getenv(variable_name)

        if value and len(value) >= 8:
            redacted = redacted.replace(
                value,
                REDACTED,
            )

    # Then catch common secret formats.
    for pattern in SECRET_PATTERNS:
        if pattern.groups:
            redacted = pattern.sub(
                rf"\1{REDACTED}",
                redacted,
            )
        else:
            redacted = pattern.sub(
                REDACTED,
                redacted,
            )

    return redacted


def redact_lines(
    lines: list[str],
) -> list[str]:
    return [
        redact_text(line) or ""
        for line in lines
    ]
