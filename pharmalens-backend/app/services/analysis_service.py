"""Background compliance-analysis execution and result persistence."""

from __future__ import annotations

import asyncio
import logging
from collections.abc import Mapping
from decimal import Decimal
from typing import Any
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.agents.compliance_pipeline import compliance_graph, create_initial_state
from app.core.database import AsyncSessionLocal
from app.models.analysis import Analysis, AnalysisGap, CorrectiveAction
from app.models.audit import AuditLog
from app.models.base import utc_now
from app.models.document import Document
from app.models.template import ComplianceTemplate, TemplateSection
from app.services.scoring import (
    ComplianceCategory,
    ComplianceScoreBreakdown,
    ComplianceScoringError,
    calculate_compliance_score,
    calculate_score_breakdown,
    categorize_compliance_score,
)


logger = logging.getLogger(__name__)

__all__ = [
    "ComplianceCategory",
    "ComplianceScoreBreakdown",
    "ComplianceScoringError",
    "calculate_compliance_score",
    "calculate_score_breakdown",
    "categorize_compliance_score",
    "launch_analysis_task",
    "recover_interrupted_analyses",
    "run_analysis_pipeline",
    "shutdown_analysis_tasks",
]

_BACKGROUND_TASKS: set[asyncio.Task[None]] = set()
_VALID_GAP_TYPES = {"missing", "incomplete", "non_compliant"}
_VALID_PRIORITIES = {"immediate", "short_term", "long_term"}


class AnalysisExecutionError(RuntimeError):
    """Indicate that a background analysis cannot be completed safely."""


async def _load_analysis(db: AsyncSession, analysis_id: UUID) -> Analysis | None:
    """Load one analysis record for background processing."""
    return await db.get(Analysis, analysis_id)


async def _load_template_with_sections(
    db: AsyncSession,
    template_id: UUID,
) -> ComplianceTemplate | None:
    """Load a template and its ordered sections in one async query."""
    result = await db.execute(
        select(ComplianceTemplate)
        .options(selectinload(ComplianceTemplate.sections))
        .where(ComplianceTemplate.id == template_id)
    )
    return result.scalar_one_or_none()


def _section_payload(section: TemplateSection) -> dict[str, object]:
    """Convert a template section ORM object into graph input data."""
    return {
        "id": str(section.id),
        "section_code": section.section_code,
        "title": section.title,
        "requirement_text": section.requirement_text,
        "mandatory": section.mandatory,
        "order_index": section.order_index,
    }


def _section_key(value: object) -> str:
    """Normalize an agent section label for template-section matching."""
    return str(value).strip().casefold()


def _template_section_index(
    sections: list[TemplateSection],
) -> dict[str, TemplateSection]:
    """Index sections by canonical code, title, and UUID string."""
    index: dict[str, TemplateSection] = {}
    for section in sections:
        index[_section_key(section.section_code)] = section
        index[_section_key(section.title)] = section
        index[_section_key(section.id)] = section
    return index


def _state_list(state: Mapping[str, Any], field_name: str) -> list[dict[str, object]]:
    """Read one validated list field from the completed graph state."""
    value = state.get(field_name, [])
    if not isinstance(value, list):
        raise AnalysisExecutionError(f"Pipeline field '{field_name}' is not a list.")
    if not all(isinstance(item, Mapping) for item in value):
        raise AnalysisExecutionError(f"Pipeline field '{field_name}' contains invalid items.")
    return [dict(item) for item in value]


def _safe_pipeline_error(state: Mapping[str, Any]) -> str:
    """Return a bounded, non-secret pipeline error for persistence and polling."""
    error = state.get("error")
    if isinstance(error, str) and error.strip():
        return error.strip()[:1000]
    return "The compliance analysis pipeline failed to complete."


async def _persist_completed_analysis(
    db: AsyncSession,
    analysis: Analysis,
    template: ComplianceTemplate,
    pipeline_state: Mapping[str, Any],
) -> None:
    """Persist graph findings, recommendations, score, and completion audit data."""
    gaps = _state_list(pipeline_state, "gaps")
    actions = _state_list(pipeline_state, "corrective_actions")
    score_breakdown = calculate_score_breakdown(gaps)
    section_index = _template_section_index(template.sections)
    persisted_gaps: list[AnalysisGap] = []
    gap_by_section: dict[str, AnalysisGap] = {}
    action_counts: dict[str, int] = {}

    for gap in gaps:
        section_label = gap.get("template_section")
        if not isinstance(section_label, str) or not section_label.strip():
            raise AnalysisExecutionError("A pipeline gap is missing its template section.")
        section_key = _section_key(section_label)
        section = section_index.get(section_key)
        if section is None:
            raise AnalysisExecutionError(
                "A pipeline gap references an unknown template section."
            )
        if section_key in gap_by_section:
            raise AnalysisExecutionError(
                "The pipeline returned multiple gaps for one template section."
            )
        severity = gap.get("severity")
        gap_type = gap.get("gap_type")
        description = gap.get("gap_description")
        document_excerpt = gap.get("document_excerpt", "")
        if not isinstance(severity, str) or not isinstance(gap_type, str):
            raise AnalysisExecutionError("A pipeline gap has invalid classification fields.")
        severity = severity.strip().lower()
        gap_type = gap_type.strip().lower()
        if gap_type not in _VALID_GAP_TYPES:
            raise AnalysisExecutionError("A pipeline gap has an invalid gap type.")
        if not isinstance(description, str):
            raise AnalysisExecutionError("A pipeline gap has an invalid description.")
        description = description.strip()
        if not description:
            raise AnalysisExecutionError("A pipeline gap is missing its description.")
        if not isinstance(document_excerpt, str):
            raise AnalysisExecutionError("A pipeline gap has an invalid document excerpt.")
        gap_record = AnalysisGap(
            analysis_id=analysis.id,
            template_section_id=section.id,
            severity=severity,
            gap_type=gap_type,
            document_excerpt=document_excerpt,
            gap_description=description,
            remediation_guidance="",
        )
        db.add(gap_record)
        persisted_gaps.append(gap_record)
        gap_by_section[section_key] = gap_record
        action_counts[section_key] = 0

    await db.flush()

    for action in actions:
        section_label = action.get("template_section")
        if not isinstance(section_label, str) or not section_label.strip():
            raise AnalysisExecutionError(
                "A corrective action is missing its template section."
            )
        section_key = _section_key(section_label)
        gap_record = gap_by_section.get(section_key)
        if gap_record is None:
            raise AnalysisExecutionError(
                "A corrective action references a section without a matching gap."
            )
        title = action.get("title")
        action_description = action.get("action_description")
        priority = action.get("priority")
        regulatory_reference = action.get("regulatory_reference", "")
        if not isinstance(title, str) or not isinstance(action_description, str):
            raise AnalysisExecutionError("A corrective action has invalid text fields.")
        if not isinstance(priority, str) or not isinstance(regulatory_reference, str):
            raise AnalysisExecutionError("A corrective action has invalid classification fields.")
        title = title.strip()
        action_description = action_description.strip()
        priority = priority.strip().lower()
        regulatory_reference = regulatory_reference.strip()
        if not title or not action_description:
            raise AnalysisExecutionError("A corrective action is missing required text.")
        if len(title) > 255 or len(regulatory_reference) > 100:
            raise AnalysisExecutionError("A corrective action contains an oversized field.")
        if priority not in _VALID_PRIORITIES:
            raise AnalysisExecutionError("A corrective action has an invalid priority.")
        db.add(
            CorrectiveAction(
                analysis_gap_id=gap_record.id,
                title=title,
                action_description=action_description,
                priority=priority,
                regulatory_reference=regulatory_reference,
            )
        )
        action_counts[section_key] += 1

    if any(count == 0 for count in action_counts.values()):
        raise AnalysisExecutionError(
            "The pipeline did not produce a corrective action for every gap."
        )
    if not gaps and actions:
        raise AnalysisExecutionError(
            "The pipeline returned corrective actions without compliance gaps."
        )

    analysis.status = "completed"
    analysis.compliance_score = Decimal(str(score_breakdown.score))
    analysis.critical_gaps_count = score_breakdown.critical_count
    analysis.major_gaps_count = score_breakdown.major_count
    analysis.minor_gaps_count = score_breakdown.minor_count
    analysis.summary = str(pipeline_state.get("summary", ""))
    analysis.error_message = None
    analysis.completed_at = utc_now()
    db.add(
        AuditLog(
            entity_type="analysis",
            entity_id=analysis.id,
            action="analysis_completed",
            metadata_json={
                "document_id": str(analysis.document_id),
                "template_id": str(analysis.template_id),
                "status": analysis.status,
                "compliance_score": score_breakdown.score,
                "category": score_breakdown.category,
                "total_gaps": len(persisted_gaps),
            },
        )
    )
    await db.commit()


async def _mark_analysis_failed(analysis_id: UUID, error_message: str) -> None:
    """Persist failure status in a fresh session after a pipeline exception."""
    try:
        async with AsyncSessionLocal() as db:
            analysis = await _load_analysis(db, analysis_id)
            if analysis is None:
                logger.error("Cannot mark missing analysis as failed: %s", analysis_id)
                return
            analysis.status = "failed"
            analysis.error_message = error_message[:1000]
            analysis.completed_at = utc_now()
            db.add(
                AuditLog(
                    entity_type="analysis",
                    entity_id=analysis.id,
                    action="analysis_failed",
                    metadata_json={"error": analysis.error_message},
                )
            )
            await db.commit()
    except Exception:
        logger.exception("Could not persist failed analysis status for %s", analysis_id)


def _safe_failure_message(error: Exception) -> str:
    """Convert internal errors into safe persisted analysis failure text."""
    if isinstance(error, AnalysisExecutionError):
        return str(error)[:1000]
    return "The compliance analysis pipeline failed. Review the server logs."


async def recover_interrupted_analyses() -> None:
    """Mark processing analyses from a previous backend process as failed."""
    try:
        async with AsyncSessionLocal() as db:
            result = await db.execute(
                select(Analysis).where(Analysis.status == "processing")
            )
            interrupted = result.scalars().all()
            if not interrupted:
                return
            completed_at = utc_now()
            for analysis in interrupted:
                analysis.status = "failed"
                analysis.error_message = (
                    "The analysis was interrupted when the backend stopped."
                )
                analysis.completed_at = completed_at
                db.add(
                    AuditLog(
                        entity_type="analysis",
                        entity_id=analysis.id,
                        action="analysis_failed",
                        metadata_json={"reason": "backend_restart"},
                    )
                )
            await db.commit()
            logger.warning(
                "Marked %d interrupted analyses as failed after backend startup.",
                len(interrupted),
            )
    except Exception:
        logger.exception("Could not recover interrupted analysis records.")


async def run_analysis_pipeline(analysis_id: UUID) -> None:
    """Load inputs, run LangGraph in a worker thread, and persist the report."""
    try:
        async with AsyncSessionLocal() as db:
            analysis = await _load_analysis(db, analysis_id)
            if analysis is None:
                raise AnalysisExecutionError("Analysis record not found.")
            if analysis.status != "processing":
                logger.info(
                    "Skipping analysis task %s because its status is %s.",
                    analysis_id,
                    analysis.status,
                )
                return
            document = await db.get(Document, analysis.document_id)
            template = await _load_template_with_sections(db, analysis.template_id)
            if document is None:
                raise AnalysisExecutionError("The analysis document no longer exists.")
            if template is None:
                raise AnalysisExecutionError("The analysis template no longer exists.")

            initial_state = create_initial_state(
                document_id=str(document.id),
                template_id=str(template.id),
                document_text=document.extracted_text,
                template_sections=[_section_payload(section) for section in template.sections],
            )
            pipeline_state = await asyncio.to_thread(
                compliance_graph.invoke,
                initial_state,
            )
            if pipeline_state.get("error"):
                raise AnalysisExecutionError(_safe_pipeline_error(pipeline_state))
            await _persist_completed_analysis(db, analysis, template, pipeline_state)
    except Exception as error:
        logger.exception("Analysis pipeline failed for analysis_id=%s", analysis_id)
        await _mark_analysis_failed(analysis_id, _safe_failure_message(error))


def _background_task_done(task: asyncio.Task[None]) -> None:
    """Release a completed task and log unexpected task-level exceptions."""
    _BACKGROUND_TASKS.discard(task)
    if task.cancelled():
        return
    error = task.exception()
    if error is not None:
        logger.error(
            "Unhandled background analysis task failure.",
            exc_info=(type(error), error, error.__traceback__),
        )


def launch_analysis_task(analysis_id: UUID) -> None:
    """Schedule an analysis without reusing the request's database session."""
    task = asyncio.create_task(
        run_analysis_pipeline(analysis_id),
        name=f"pharmalens-analysis-{analysis_id}",
    )
    _BACKGROUND_TASKS.add(task)
    task.add_done_callback(_background_task_done)


async def shutdown_analysis_tasks() -> None:
    """Cancel outstanding analyses before the database pool is disposed."""
    tasks = tuple(_BACKGROUND_TASKS)
    for task in tasks:
        task.cancel()
    if tasks:
        await asyncio.gather(*tasks, return_exceptions=True)
