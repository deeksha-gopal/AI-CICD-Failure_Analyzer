from app.analyzer import analyze_demo


def test_detects_missing_module():
    result = analyze_demo("Traceback\nModuleNotFoundError: No module named 'requests'")
    assert result.findings[0].category == "dependencies"
    assert "ModuleNotFoundError" in result.findings[0].evidence


def test_multiple_failures_are_detected():
    result = analyze_demo("ERROR: Permission denied\nFAILED tests/test_app.py::test_login - AssertionError")
    assert {f.category for f in result.findings} == {"permissions", "testing"}


def test_unknown_log_is_not_overconfident():
    result = analyze_demo("Pipeline exited unexpectedly")
    assert result.findings[0].category == "unclassified"
    assert "manual" in result.summary.lower()


def test_docker_error_detected():
    result = analyze_demo("ERROR: failed to solve: process /bin/sh failed")
    assert "container" in {f.category for f in result.findings}
