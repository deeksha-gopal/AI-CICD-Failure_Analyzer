"""Best-effort secret redaction before persistence or sending data to an LLM.

Do not assume regex filtering catches every secret. Avoid uploading sensitive logs.
"""
import re

MASK = "[REDACTED]"

# Common, recognizable provider token patterns.
TOKEN_PATTERNS = [
    re.compile(r"\bgh(?:p|o|u|s|r)_[A-Za-z0-9_]{20,}\b"),
    re.compile(r"\bgithub_pat_[A-Za-z0-9_]{20,}\b"),
    re.compile(r"\bAKIA[0-9A-Z]{16}\b"),
    re.compile(r"\bsk-[A-Za-z0-9_-]{16,}\b"),
]

# Log lines that leak authorization headers or common secret settings.
HEADER_RE = re.compile(r"(?im)(\bauthorization\s*:\s*bearer\s+)\S+")
ASSIGNMENT_RE = re.compile(
    r"(?im)(\b(?:api[_-]?key|access[_-]?token|secret|password|token)\b\s*[:=]\s*)"
    r"(?:\"[^\"\n]*\"|'[^'\n]*'|[^\s,;]+)"
)


def redact_secrets(text: str) -> str:
    output = text
    for pattern in TOKEN_PATTERNS:
        output = pattern.sub(MASK, output)
    output = HEADER_RE.sub(lambda m: m.group(1) + MASK, output)
    output = ASSIGNMENT_RE.sub(lambda m: m.group(1) + MASK, output)
    return output
