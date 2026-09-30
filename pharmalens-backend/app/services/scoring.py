"""Deterministic compliance scoring used by the analysis pipeline."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from typing import Literal


ComplianceCategory = Literal[
    "High Compliance",
    "Moderate Risk",
    "Critical Non-Compliance",
]
GapSeverity = Literal["critical", "major", "minor"]


class ComplianceScoringError(ValueError):
    """Indicate that a gap cannot be scored because its severity is invalid."""


@dataclass(frozen=True, slots=True)
class ComplianceScoreBreakdown:
    """Contain the weighted score, category, and severity counts."""

    score: float
    category: ComplianceCategory
    critical_count: int
    major_count: int
    minor_count: int


def categorize_compliance_score(score: float) -> ComplianceCategory:
    """Convert a bounded score into the product's displayed compliance category."""
    if not 0.0 <= score <= 100.0:
        raise ComplianceScoringError("Compliance score must be between 0 and 100.")
    if score >= 90.0:
        return "High Compliance"
    if score >= 70.0:
        return "Moderate Risk"
    return "Critical Non-Compliance"


def calculate_score_breakdown(
    gaps: Sequence[Mapping[str, object]],
) -> ComplianceScoreBreakdown:
    """Apply the weighted critical/major/minor penalty formula to gap findings."""
    severity_counts: dict[GapSeverity, int] = {
        "critical": 0,
        "major": 0,
        "minor": 0,
    }
    for gap in gaps:
        raw_severity = gap.get("severity")
        if not isinstance(raw_severity, str):
            raise ComplianceScoringError("Every gap must contain a text severity.")
        severity = raw_severity.strip().lower()
        if severity not in severity_counts:
            raise ComplianceScoringError(
                "Gap severity must be one of: critical, major, or minor."
            )
        severity_counts[severity] += 1

    penalty = (
        severity_counts["critical"] * 25
        + severity_counts["major"] * 10
        + severity_counts["minor"] * 3
    )
    score = round(max(0.0, 100.0 - penalty), 2)
    return ComplianceScoreBreakdown(
        score=score,
        category=categorize_compliance_score(score),
        critical_count=severity_counts["critical"],
        major_count=severity_counts["major"],
        minor_count=severity_counts["minor"],
    )


def calculate_compliance_score(gaps: Sequence[Mapping[str, object]]) -> float:
    """Return only the numeric score for callers that do not need the breakdown."""
    return calculate_score_breakdown(gaps).score
