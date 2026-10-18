import json
import logging

from app.logging_config import (
    JsonFormatter,
)


def test_json_formatter_includes_structured_fields():
    formatter = JsonFormatter()

    record = logging.LogRecord(
        name="deploypilot",
        level=logging.INFO,
        pathname=__file__,
        lineno=10,
        msg="Deployment status collected",
        args=(),
        exc_info=None,
    )

    record.event = "deployment_status"
    record.run_id = 123
    record.status = "passed"

    result = formatter.format(
        record
    )

    data = json.loads(
        result
    )

    assert (
        data["message"]
        == "Deployment status collected"
    )

    assert (
        data["event"]
        == "deployment_status"
    )

    assert data["run_id"] == 123
    assert data["status"] == "passed"
    assert data["level"] == "INFO"
