"""Response models shared conceptually with frontend/src/types.ts."""
from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field


class Finding(BaseModel):
    category: str = Field(max_length=64)
    severity: Literal["high", "medium", "low"] = "medium"
    title: str = Field(max_length=150)
    evidence: str = Field(max_length=300)
    explanation: str = Field(max_length=1000)
    recommendations: list[str] = Field(default_factory=list, max_length=5)


class AnalysisResult(BaseModel):
    summary: str = Field(max_length=1200)
    findings: list[Finding] = Field(default_factory=list, max_length=8)
    next_steps: list[str] = Field(default_factory=list, max_length=6)


class AnalysisResponse(AnalysisResult):
    id: str
    created_at: datetime
    filename: str
    mode: Literal["demo", "llm"]
    redacted_excerpt: str
    duration_ms: int


class HistoryItem(BaseModel):
    id: str
    created_at: datetime
    filename: str
    mode: Literal["demo", "llm"]
    summary: str
    finding_count: int
