"""Compliance-analysis trigger, status, history, and report endpoints."""

from __future__ import annotations

import logging
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import func, select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.database import get_db
from app.models.analysis import Analysis, AnalysisGap
from app.models.audit import AuditLog
from app.models.base import utc_now
from app.models.document import Document
from app.models.template import ComplianceTemplate
from app.schemas.analysis import (
    AnalysisAcceptedResponse,
    AnalysisCollectionResponse,
    AnalysisCreateRequest,
    AnalysisDocumentResponse,
    AnalysisGapResponse,
    AnalysisReportResponse,
    AnalysisStatus,
    AnalysisSummaryResponse,
    AnalysisTemplateResponse,
    CorrectiveActionResponse,
)
from app.services.analysis_service import launch_analysis_task


router = APIRouter(prefix="/api/analyses", tags=["analyses"])
logger = logging.getLogger(__name__)


async def _load_analysis_report(
    db: AsyncSession,
    analysis_id: UUID,
) -> Analysis | None:
    """Load an analysis and all relationships required for its report."""
    result = await db.execute(
        select(Analysis)
        .options(
            selectinload(Analysis.document),
            selectinload(Analysis.template),
            selectinload(Analysis.gaps).selectinload(AnalysisGap.template_section),
            selectinload(Analysis.gaps).selectinload(AnalysisGap.corrective_actions),
        )
        .where(Analysis.id == analysis_id)
    )
    return result.scalar_one_or_none()


def _report_response(analysis: Analysis) -> AnalysisReportResponse:
    """Convert a fully loaded analysis ORM object into its report schema."""
    if analysis.document is None or analysis.template is None:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="The analysis relationships could not be loaded",
        )

    gaps = [
        AnalysisGapResponse(
            id=gap.id,
            template_section_id=gap.template_section_id,
            section_name=gap.template_section.title if gap.template_section else None,
            severity=gap.severity,
            gap_type=gap.gap_type,
            document_excerpt=gap.document_excerpt,
            gap_description=gap.gap_description,
            remediation_guidance=gap.remediation_guidance,
            corrective_actions=[
                CorrectiveActionResponse(
                    id=action.id,
                    analysis_gap_id=action.analysis_gap_id,
                    title=action.title,
                    action_description=action.action_description,
                    priority=action.priority,
                    regulatory_reference=action.regulatory_reference,
                )
                for action in gap.corrective_actions
            ],
        )
        for gap in analysis.gaps
    ]
    return AnalysisReportResponse(
        id=analysis.id,
        document=AnalysisDocumentResponse(
            id=analysis.document.id,
            filename=analysis.document.filename,
            file_type=analysis.document.file_type,
        ),
        template=AnalysisTemplateResponse(
            id=analysis.template.id,
            name=analysis.template.name,
            version=analysis.template.version,
            governing_body=analysis.template.governing_body,
        ),
        status=analysis.status,
        compliance_score=(
            float(analysis.compliance_score)
            if analysis.compliance_score is not None
            else None
        ),
        critical_gaps_count=analysis.critical_gaps_count,
        major_gaps_count=analysis.major_gaps_count,
        minor_gaps_count=analysis.minor_gaps_count,
        summary=analysis.summary,
        error_message=analysis.error_message,
        started_at=analysis.started_at,
        completed_at=analysis.completed_at,
        created_at=analysis.created_at,
        updated_at=analysis.updated_at,
        gaps=gaps,
    )


def _summary_response(analysis: Analysis) -> AnalysisSummaryResponse:
    """Convert an analysis ORM object into a history item schema."""
    return AnalysisSummaryResponse(
        id=analysis.id,
        document_id=analysis.document_id,
        template_id=analysis.template_id,
        status=analysis.status,
        compliance_score=(
            float(analysis.compliance_score)
            if analysis.compliance_score is not None
            else None
        ),
        critical_gaps_count=analysis.critical_gaps_count,
        major_gaps_count=analysis.major_gaps_count,
        minor_gaps_count=analysis.minor_gaps_count,
        summary=analysis.summary,
        error_message=analysis.error_message,
        started_at=analysis.started_at,
        completed_at=analysis.completed_at,
        created_at=analysis.created_at,
        updated_at=analysis.updated_at,
    )


@router.post(
    "",
    response_model=AnalysisAcceptedResponse,
    status_code=status.HTTP_202_ACCEPTED,
)
async def create_analysis(
    payload: AnalysisCreateRequest,
    db: AsyncSession = Depends(get_db),
) -> AnalysisAcceptedResponse:
    """Create a processing record and launch its background pipeline."""
    document = await db.get(Document, payload.document_id)
    if document is None:
        raise HTTPException(status_code=404, detail="Document not found")

    template = await db.get(ComplianceTemplate, payload.template_id)
    if template is None:
        raise HTTPException(status_code=404, detail="Compliance template not found")

    analysis = Analysis(
        document_id=document.id,
        template_id=template.id,
        status="processing",
        started_at=utc_now(),
    )
    db.add(analysis)
    await db.flush()
    db.add(
        AuditLog(
            entity_type="analysis",
            entity_id=analysis.id,
            action="analysis_triggered",
            metadata_json={
                "document_id": str(document.id),
                "template_id": str(template.id),
                "status": analysis.status,
            },
        )
    )
    try:
        await db.commit()
    except SQLAlchemyError as error:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error",
        ) from error

    try:
        launch_analysis_task(analysis.id)
    except Exception as error:
        logger.exception("Could not start analysis task for id=%s", analysis.id)
        analysis.status = "failed"
        analysis.error_message = "The compliance analysis could not be started."
        analysis.completed_at = utc_now()
        db.add(
            AuditLog(
                entity_type="analysis",
                entity_id=analysis.id,
                action="analysis_failed",
                metadata_json={"reason": "task_start_failure"},
            )
        )
        try:
            await db.commit()
        except SQLAlchemyError:
            await db.rollback()
            logger.exception("Could not persist task-start failure for id=%s", analysis.id)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="The compliance analysis could not be started",
        ) from error
    return AnalysisAcceptedResponse(analysis_id=analysis.id, status="processing")


@router.get("", response_model=AnalysisCollectionResponse)
async def list_analyses(
    document_id: UUID | None = Query(default=None),
    analysis_status: AnalysisStatus | None = Query(default=None, alias="status"),
    page: int = Query(default=1, ge=1),
    limit: int = Query(default=10, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
) -> AnalysisCollectionResponse:
    """Return paginated analysis history with optional document/status filters."""
    filters = []
    if document_id is not None:
        filters.append(Analysis.document_id == document_id)
    if analysis_status is not None:
        filters.append(Analysis.status == analysis_status)

    total = int(
        await db.scalar(
            select(func.count()).select_from(Analysis).where(*filters)
        )
        or 0
    )
    result = await db.execute(
        select(Analysis)
        .where(*filters)
        .order_by(Analysis.created_at.desc(), Analysis.id.desc())
        .offset((page - 1) * limit)
        .limit(limit)
    )
    return AnalysisCollectionResponse(
        items=[_summary_response(analysis) for analysis in result.scalars().all()],
        page=page,
        limit=limit,
        total=total,
    )


@router.get("/{analysis_id}", response_model=AnalysisReportResponse)
async def get_analysis(
    analysis_id: UUID,
    db: AsyncSession = Depends(get_db),
) -> AnalysisReportResponse:
    """Return current analysis status or its completed report."""
    analysis = await _load_analysis_report(db, analysis_id)
    if analysis is None:
        raise HTTPException(status_code=404, detail="Analysis not found")
    return _report_response(analysis)
