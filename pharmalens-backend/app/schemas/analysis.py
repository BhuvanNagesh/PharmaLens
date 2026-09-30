"""Pydantic schemas for compliance-analysis requests and reports."""

from __future__ import annotations

from datetime import datetime
from typing import Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


AnalysisStatus = Literal["pending", "processing", "completed", "failed"]


class AnalysisCreateRequest(BaseModel):
    """Identify the document and regulatory template to analyze."""

    document_id: UUID
    template_id: UUID


class AnalysisAcceptedResponse(BaseModel):
    """Confirm that a background analysis task was created."""

    analysis_id: UUID
    status: Literal["processing"]


class AnalysisDocumentResponse(BaseModel):
    """Return document context included in an analysis report."""

    id: UUID
    filename: str
    file_type: Literal["pdf", "docx"]


class AnalysisTemplateResponse(BaseModel):
    """Return template context included in an analysis report."""

    id: UUID
    name: str
    version: str
    governing_body: str


class CorrectiveActionResponse(BaseModel):
    """Return one persisted corrective-action recommendation."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    analysis_gap_id: UUID
    title: str
    action_description: str
    priority: Literal["immediate", "short_term", "long_term"]
    regulatory_reference: str


class AnalysisGapResponse(BaseModel):
    """Return one persisted gap and its recommendations."""

    id: UUID
    template_section_id: UUID | None
    section_name: str | None
    severity: Literal["critical", "major", "minor"]
    gap_type: Literal["missing", "incomplete", "non_compliant"]
    document_excerpt: str
    gap_description: str
    remediation_guidance: str
    corrective_actions: list[CorrectiveActionResponse]


class AnalysisReportResponse(BaseModel):
    """Return the complete analysis status or completed compliance report."""

    id: UUID
    document: AnalysisDocumentResponse
    template: AnalysisTemplateResponse
    status: AnalysisStatus
    compliance_score: float | None = Field(default=None, ge=0, le=100)
    critical_gaps_count: int = Field(ge=0)
    major_gaps_count: int = Field(ge=0)
    minor_gaps_count: int = Field(ge=0)
    summary: str
    error_message: str | None
    started_at: datetime | None
    completed_at: datetime | None
    created_at: datetime
    updated_at: datetime
    gaps: list[AnalysisGapResponse]


class AnalysisSummaryResponse(BaseModel):
    """Return one analysis item in history responses."""

    id: UUID
    document_id: UUID
    template_id: UUID
    status: AnalysisStatus
    compliance_score: float | None = Field(default=None, ge=0, le=100)
    critical_gaps_count: int = Field(ge=0)
    major_gaps_count: int = Field(ge=0)
    minor_gaps_count: int = Field(ge=0)
    summary: str
    error_message: str | None
    started_at: datetime | None
    completed_at: datetime | None
    created_at: datetime
    updated_at: datetime


class AnalysisCollectionResponse(BaseModel):
    """Return paginated analysis history."""

    items: list[AnalysisSummaryResponse]
    page: int = Field(ge=1)
    limit: int = Field(ge=1, le=100)
    total: int = Field(ge=0)
