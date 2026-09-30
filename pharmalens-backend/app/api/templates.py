"""Compliance-template creation, retrieval, update, and deletion endpoints."""

from __future__ import annotations

import logging
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.database import get_db
from app.models.analysis import Analysis
from app.models.audit import AuditLog
from app.models.template import ComplianceTemplate, TemplateSection
from app.schemas.template import (
    TemplateCollectionResponse,
    TemplateCreateRequest,
    TemplateResponse,
    TemplateSectionResponse,
    TemplateSummaryResponse,
    TemplateUpdateRequest,
)


logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/templates", tags=["templates"])


async def _load_template(
    db: AsyncSession,
    template_id: UUID,
) -> ComplianceTemplate | None:
    """Load one template and its ordered sections."""
    result = await db.execute(
        select(ComplianceTemplate)
        .options(selectinload(ComplianceTemplate.sections))
        .where(ComplianceTemplate.id == template_id)
    )
    return result.scalar_one_or_none()


def _template_response(template: ComplianceTemplate) -> TemplateResponse:
    """Convert a loaded ORM template to its response schema."""
    return TemplateResponse(
        id=template.id,
        name=template.name,
        version=template.version,
        description=template.description,
        governing_body=template.governing_body,
        sections=[
            TemplateSectionResponse.model_validate(section)
            for section in template.sections
        ],
        created_at=template.created_at,
        updated_at=template.updated_at,
    )


def _template_summary(template: ComplianceTemplate) -> TemplateSummaryResponse:
    """Convert a loaded ORM template to a collection summary."""
    return TemplateSummaryResponse(
        id=template.id,
        name=template.name,
        version=template.version,
        description=template.description,
        governing_body=template.governing_body,
        section_count=len(template.sections),
        created_at=template.created_at,
        updated_at=template.updated_at,
    )


def _build_sections(template_id: UUID, sections: list) -> list[TemplateSection]:
    """Build ORM sections from validated request data."""
    return [
        TemplateSection(
            template_id=template_id,
            section_code=section.section_code,
            title=section.title,
            requirement_text=section.requirement_text,
            mandatory=section.mandatory,
            order_index=section.order_index,
        )
        for section in sections
    ]


@router.post("", response_model=TemplateResponse, status_code=status.HTTP_201_CREATED)
async def create_template(
    payload: TemplateCreateRequest,
    db: AsyncSession = Depends(get_db),
) -> TemplateResponse:
    """Create a compliance template with at least one normative section."""
    template = ComplianceTemplate(
        name=payload.name,
        version=payload.version,
        description=payload.description,
        governing_body=payload.governing_body,
    )
    db.add(template)

    try:
        await db.flush()
        sections = _build_sections(template.id, payload.sections)
        db.add_all(sections)
        db.add(
            AuditLog(
                entity_type="template",
                entity_id=template.id,
                action="created",
                metadata_json={
                    "name": template.name,
                    "version": template.version,
                    "governing_body": template.governing_body,
                },
            )
        )
        await db.commit()
        persisted_template = await _load_template(db, template.id)
        if persisted_template is None:
            raise HTTPException(
                status_code=500,
                detail="The compliance template could not be loaded after creation",
            )
        return _template_response(persisted_template)
    except IntegrityError as error:
        await db.rollback()
        logger.exception("Template creation violated a database constraint.")
        raise HTTPException(
            status_code=400,
            detail="The compliance template could not be created",
        ) from error
    except SQLAlchemyError as error:
        await db.rollback()
        logger.exception("Template creation failed.")
        raise HTTPException(status_code=500, detail="Internal server error") from error


@router.get("", response_model=TemplateCollectionResponse)
async def list_templates(
    page: int = Query(default=1, ge=1),
    limit: int = Query(default=10, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
) -> TemplateCollectionResponse:
    """Return paginated compliance-template metadata."""
    total = int(
        await db.scalar(select(func.count()).select_from(ComplianceTemplate)) or 0
    )
    result = await db.execute(
        select(ComplianceTemplate)
        .options(selectinload(ComplianceTemplate.sections))
        .order_by(ComplianceTemplate.created_at.asc(), ComplianceTemplate.id.asc())
        .offset((page - 1) * limit)
        .limit(limit)
    )
    templates = result.scalars().all()
    return TemplateCollectionResponse(
        items=[_template_summary(template) for template in templates],
        page=page,
        limit=limit,
        total=total,
    )


@router.get("/{template_id}", response_model=TemplateResponse)
async def get_template(
    template_id: UUID,
    db: AsyncSession = Depends(get_db),
) -> TemplateResponse:
    """Return one compliance template with all normative sections."""
    template = await _load_template(db, template_id)
    if template is None:
        raise HTTPException(status_code=404, detail="Compliance template not found")
    return _template_response(template)


@router.put("/{template_id}", response_model=TemplateResponse)
async def update_template(
    template_id: UUID,
    payload: TemplateUpdateRequest,
    db: AsyncSession = Depends(get_db),
) -> TemplateResponse:
    """Replace a compliance template and its normative sections."""
    template = await _load_template(db, template_id)
    if template is None:
        raise HTTPException(status_code=404, detail="Compliance template not found")

    template.name = payload.name
    template.version = payload.version
    template.description = payload.description
    template.governing_body = payload.governing_body
    template.sections = _build_sections(template.id, payload.sections)

    try:
        db.add_all(template.sections)
        db.add(
            AuditLog(
                entity_type="template",
                entity_id=template.id,
                action="updated",
                metadata_json={"name": template.name, "version": template.version},
            )
        )
        await db.commit()
        return _template_response(template)
    except IntegrityError as error:
        await db.rollback()
        logger.exception("Template update violated a database constraint.")
        raise HTTPException(
            status_code=400,
            detail="The compliance template could not be updated",
        ) from error
    except SQLAlchemyError as error:
        await db.rollback()
        logger.exception("Template update failed for id=%s", template_id)
        raise HTTPException(status_code=500, detail="Internal server error") from error


@router.delete(
    "/{template_id}",
    response_model=None,
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_template(
    template_id: UUID,
    db: AsyncSession = Depends(get_db),
) -> None:
    """Delete an unused compliance template while preserving its audit event."""
    template = await db.get(ComplianceTemplate, template_id)
    if template is None:
        raise HTTPException(status_code=404, detail="Compliance template not found")

    analysis_count = int(
        await db.scalar(
            select(func.count())
            .select_from(Analysis)
            .where(Analysis.template_id == template_id)
        )
        or 0
    )
    if analysis_count:
        raise HTTPException(
            status_code=400,
            detail="The compliance template cannot be deleted because analyses reference it",
        )

    try:
        db.add(
            AuditLog(
                entity_type="template",
                entity_id=template.id,
                action="deleted",
                metadata_json={"name": template.name, "version": template.version},
            )
        )
        await db.delete(template)
        await db.commit()
    except IntegrityError as error:
        await db.rollback()
        logger.exception("Template deletion violated a database constraint.")
        raise HTTPException(
            status_code=400,
            detail="The compliance template cannot be deleted because it is in use",
        ) from error
    except SQLAlchemyError as error:
        await db.rollback()
        logger.exception("Template deletion failed for id=%s", template_id)
        raise HTTPException(status_code=500, detail="Internal server error") from error
