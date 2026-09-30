"""Structured Pydantic outputs returned by the compliance agents."""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


class ParsedSection(BaseModel):
    """Represent one logically extracted section from an uploaded document."""

    model_config = ConfigDict(extra="forbid")

    section_title: str = Field(min_length=1, max_length=255)
    section_content: str = Field(min_length=1)


class DocumentParserOutput(BaseModel):
    """Return all sections identified by the document parser agent."""

    model_config = ConfigDict(extra="forbid")

    sections: list[ParsedSection] = Field(default_factory=list)


class SectionMapping(BaseModel):
    """Map one required regulatory section to an extracted document section."""

    model_config = ConfigDict(extra="forbid")

    template_section: str = Field(min_length=1, max_length=255)
    matched_document_section: str | None = Field(default=None, max_length=255)
    match_confidence: Literal["high", "medium", "low", "none"]
    rationale: str = Field(default="")


class RegulatoryMappingOutput(BaseModel):
    """Return the complete template-to-document mapping."""

    model_config = ConfigDict(extra="forbid")

    mappings: list[SectionMapping] = Field(default_factory=list)


class GapFinding(BaseModel):
    """Describe one compliance gap and its severity."""

    model_config = ConfigDict(extra="forbid")

    template_section: str = Field(min_length=1, max_length=255)
    severity: Literal["critical", "major", "minor"]
    gap_type: Literal["missing", "incomplete", "non_compliant"]
    document_excerpt: str = Field(default="")
    gap_description: str = Field(min_length=1)
    regulatory_citation: str = Field(default="", max_length=100)


class GapAnalysisOutput(BaseModel):
    """Return all gaps identified by the risk-classification agent."""

    model_config = ConfigDict(extra="forbid")

    gaps: list[GapFinding] = Field(default_factory=list)


class CorrectiveAction(BaseModel):
    """Provide one actionable remediation for a compliance gap."""

    model_config = ConfigDict(extra="forbid")

    template_section: str = Field(min_length=1, max_length=255)
    title: str = Field(min_length=1, max_length=255)
    action_description: str = Field(min_length=1)
    priority: Literal["immediate", "short_term", "long_term"]
    regulatory_reference: str = Field(default="", max_length=100)


class CorrectiveActionOutput(BaseModel):
    """Return recommendations and an executive summary for the analysis."""

    model_config = ConfigDict(extra="forbid")

    summary: str = Field(default="")
    actions: list[CorrectiveAction] = Field(default_factory=list)
