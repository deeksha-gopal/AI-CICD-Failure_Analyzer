from app.redaction import redact_secrets


def test_redacts_common_credentials():
    log = (
        "Authorization: Bearer super-sensitive-value\n"
        "API_KEY=hello-world\n"
        "password='temporary secret'\n"
        "sk-abcdefghijklmnopqrstuvw\n"
        "ghp_" + "a" * 36
    )
    result = redact_secrets(log)
    for secret in ["super-sensitive-value", "hello-world", "temporary secret", "sk-abcdefghijklmnopqrstuvw", "ghp_" + "a" * 36]:
        assert secret not in result
    assert result.count("[REDACTED]") == 5
