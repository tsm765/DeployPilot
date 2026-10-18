from app.redaction import (
    REDACTED,
    redact_lines,
    redact_text,
)


def test_redacts_known_environment_secret(
    monkeypatch,
):
    monkeypatch.setenv(
        "GITHUB_TOKEN",
        "github_pat_this_is_a_fake_test_token_12345",
    )

    text = (
        "Token is "
        "github_pat_this_is_a_fake_test_token_12345"
    )

    result = redact_text(text)

    assert (
        "github_pat_this_is_a_fake_test_token_12345"
        not in result
    )

    assert REDACTED in result


def test_redacts_openai_style_key():
    text = (
        "OPENAI_API_KEY="
        "sk-fakeexample12345678901234567890"
    )

    result = redact_text(text)

    assert (
        "sk-fakeexample12345678901234567890"
        not in result
    )


def test_redacts_authorization_header():
    text = (
        "Authorization: Bearer "
        "super-secret-access-token"
    )

    result = redact_text(text)

    assert (
        "super-secret-access-token"
        not in result
    )

    assert REDACTED in result


def test_redacts_password_assignment():
    text = "password=my-secret-password"

    result = redact_text(text)

    assert (
        "my-secret-password"
        not in result
    )


def test_redacts_sensitive_query_parameter():
    text = (
        "https://example.test/resource"
        "?sig=super-secret-signature"
        "&mode=test"
    )

    result = redact_text(text)

    assert (
        "super-secret-signature"
        not in result
    )

    assert "mode=test" in result


def test_preserves_normal_log_text():
    text = (
        "FAILED tests/test_main.py::test_root "
        "- AssertionError"
    )

    assert redact_text(text) == text


def test_redacts_multiple_log_lines():
    lines = [
        "Running tests",
        "token=my-secret-token",
        "1 failed",
    ]

    result = redact_lines(lines)

    assert result[0] == "Running tests"
    assert "my-secret-token" not in result[1]
    assert result[2] == "1 failed"
