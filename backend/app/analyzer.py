"""Explainable rule-based demo analyzer; no AI key needed.

This is a teaching/demo engine, not an ML model. Its findings are hypotheses,
not proof of root cause. A real LLM can optionally be enabled in app/llm.py.
"""
import re
from dataclasses import dataclass

from .schemas import AnalysisResult, Finding


@dataclass(frozen=True)
class Rule:
    category: str
    title: str
    pattern: str
    severity: str
    explanation: str
    recommendations: tuple[str, ...]


RULES = [
    Rule(
        "dependencies", "Missing module or dependency",
        r"(?:ModuleNotFoundError|ImportError: No module named|Cannot find module|Module not found)",
        "high", "A module could not be imported or located in the build environment.",
        ("Check dependency declarations and lockfiles.",
         "Confirm the correct environment and package installation step are used.",
         "Reproduce the import failure locally or in the CI container."),
    ),
    Rule(
        "dependencies", "Package version conflict",
        r"(?:ERESOLVE|dependency conflict|ResolutionImpossible|Could not resolve dependency)",
        "high", "The package manager could not resolve compatible dependency versions.",
        ("Inspect conflicting constraints in the error details.",
         "Update or pin compatible dependencies and regenerate the lockfile.",
         "Use a clean install to confirm the fix."),
    ),
    Rule(
        "testing", "Test assertion or test-suite failure",
        r"(?:AssertionError|\bFAILED\s+[^\n]+|Tests failed|[1-9]\d* failing)",
        "high", "A test failed; the failing assertion and surrounding context should be inspected.",
        ("Run the failing test in isolation with verbose logs.",
         "Compare expected and actual output and inspect recent code changes.",
         "Add a regression test after fixing the underlying issue."),
    ),
    Rule(
        "container", "Docker build failure",
        r"(?:failed to solve|COPY failed|docker build.*failed|executor failed running)",
        "high", "A Docker image build step failed, possibly due to files, packages, or execution errors.",
        ("Inspect the failed Dockerfile layer and full build output.",
         "Verify paths in COPY commands and the Docker build context.",
         "Rebuild with --no-cache when investigating stale layers."),
    ),
    Rule(
        "permissions", "Permission or access denied",
        r"(?:Permission denied|\bEACCES\b|\bEPERM\b|403 Forbidden)",
        "medium", "The process could not access a required file, resource, or service.",
        ("Check filesystem permissions and execution identity.",
         "Check access scopes or credentials without printing secrets.",
         "Apply least-privilege permission changes."),
    ),
    Rule(
        "memory", "Possible out-of-memory termination",
        r"(?:out of memory|oom.kill|OOMKilled|exit code 137|Killed process \d+)",
        "high", "The process may have exceeded its memory limit or been killed by the system.",
        ("Inspect container or runner memory limits and peak resource use.",
         "Profile allocations and review dataset or batch sizes.",
         "Retry with monitoring to confirm the failure mechanism."),
    ),
    Rule(
        "network", "Network timeout or connection failure",
        r"(?:ETIMEDOUT|Connection timed out|ReadTimeout|Connection refused|Temporary failure in name resolution)",
        "medium", "A dependent network service could not be reached reliably.",
        ("Check DNS, service availability, and CI network rules.",
         "Set bounded retries and sensible request timeouts.",
         "Inspect the service endpoint and credentials in a safe way."),
    ),
    Rule(
        "lint", "Static analysis or formatting failure",
        r"(?:ruff check.*failed|eslint.*error|prettier.*failed|flake8.*error|lint errors?)",
        "low", "A code-quality check failed and may be blocking the pipeline.",
        ("Run the linter locally using the CI version.",
         "Fix the indicated files and keep configuration consistent.",
         "Run tests and static checks before pushing the change."),
    ),
]


def select_evidence(log: str, match: re.Match[str]) -> str:
    """Return the matching line, capped so results don't flood the UI."""
    line_start = log.rfind("\n", 0, match.start()) + 1
    line_end = log.find("\n", match.end())
    if line_end == -1:
        line_end = len(log)
    return log[line_start:line_end].strip()[:300]


def get_excerpt(log: str, limit: int = 3500) -> str:
    """Keep tail of an already-redacted log (often where CI errors appear)."""
    if len(log) <= limit:
        return log
    return "[... earlier lines omitted ...]\n" + log[-limit:]


def analyze_demo(log: str) -> AnalysisResult:
    findings: list[Finding] = []
    for rule in RULES:
        match = re.search(rule.pattern, log, re.IGNORECASE)
        if match:
            findings.append(Finding(
                category=rule.category,
                severity=rule.severity,
                title=rule.title,
                evidence=select_evidence(log, match),
                explanation=rule.explanation,
                recommendations=list(rule.recommendations),
            ))

    if not findings:
        evidence = next((line.strip() for line in reversed(log.splitlines()) if line.strip()), "No details")
        findings.append(Finding(
            category="unclassified", severity="low", title="No known failure signature matched",
            evidence=evidence[:300],
            explanation="The demo analyzer cannot determine the root cause from this log.",
            recommendations=[
                "Find the first error and the CI step that failed.",
                "Reproduce the failing command locally with verbose logging.",
                "Use LLM mode for additional hypotheses, then verify them independently.",
            ],
        ))
    return AnalysisResult(
        summary=(f"Detected {len(findings)} possible failure pattern(s). Review evidence before applying fixes."
                 if findings[0].category != "unclassified" else
                 "No known failure pattern detected; manual investigation is recommended."),
        findings=findings[:8],
        next_steps=["Open the failed CI step and inspect the earliest relevant error.",
                    "Validate the proposed change locally and rerun the pipeline.",
                    "Document the confirmed cause and add a regression check."],
    )
