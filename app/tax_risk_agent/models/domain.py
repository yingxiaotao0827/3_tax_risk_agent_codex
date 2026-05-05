from enum import Enum
from pathlib import Path
from typing import Any

from pydantic import BaseModel, Field


class RiskLevel(str, Enum):
    low = "low"
    medium = "medium"
    high = "high"
    review_required = "review_required"


class Evidence(BaseModel):
    source: str
    summary: str
    data: dict[str, Any] = Field(default_factory=dict)
    confidence: float = 0.7


class RiskHypothesis(BaseModel):
    code: str
    title: str
    reason: str
    confidence: float = 0.5
    evidence: list[Evidence] = Field(default_factory=list)


class RiskFinding(BaseModel):
    code: str
    title: str
    level: RiskLevel
    conclusion: str
    evidence: list[Evidence]
    suggestions: list[str]


class DiagnosticRequest(BaseModel):
    company_id: str
    period: str


class DiagnosticResult(BaseModel):
    company_id: str
    period: str
    executive_summary: str = ""
    findings: list[RiskFinding]
    reasoning_trace: list[str]
    report_path: Path | None = None
    chart_paths: list[Path] = Field(default_factory=list)
    needs_human_review: bool = False
