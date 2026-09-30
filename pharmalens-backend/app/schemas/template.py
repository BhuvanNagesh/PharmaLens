"""Pydantic schemas for compliance-template endpoints."""

from __future__ import annotations

import re
from collections.abc import Mapping
from datetime import datetime
from typing import Literal
from uuid import UUID

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    computed_field,
    field_validator,
    model_validator,
)


GoverningBody = Literal["FDA", "EMA", "WHO", "ICH"]


def _strip_text(value: object) -> str:
    """Normalize a required text field and reject non-string values."""
    if not isinstance(value, str):
        raise ValueError("Text fields must be strings.")
    return value.strip()


def _governing_body_from_framework(framework: str) -> str | None:
    """Map a legacy framework label to the canonical governing-body value."""
    normalized = framework.strip().upper()
    if normalized.startswith("FDA"):
        return "FDA"
    if normalized.startswith("EMA") or normalized.startswith("EU GMP"):
        return "EMA"
    if normalized.startswith("WHO"):
        return "WHO"
    if normalized.startswith("ICH"):
        return "ICH"
    return None


def _derived_section_code(title: str) -> str:
    """Create a stable bounded code when a legacy section omits one."""
    slug = re.sub(r"[^a-z0-9]+", "-", title.lower()).strip("-")
    return f"custom-{slug or 'section'}"[:50]


class TemplateSectionRequest(BaseModel):
    """Validate one canonical or legacy normative section payload."""

    section_code: str = Field(default="", max_length=50)
    title: str = Field(default="", max_length=255)
    requirement_text: str = Field(default="")
    mandatory: bool = True
    order_index: int = Field(default=0, ge=0)

    @model_validator(mode="before")
    @classmethod
    def normalize_legacy_fields(cls, data: object) -> object:
        """Translate legacy section names without changing the database schema."""
        if not isinstance(data, Mapping):
            return data

        values = dict(data)
        if not values.get("title") and values.get("section_name"):
            values["title"] = values["section_name"]
        if not values.get("requirement_text") and values.get("description"):
            values["requirement_text"] = values["description"]
        if "mandatory" not in values and "is_mandatory" in values:
            values["mandatory"] = values["is_mandatory"]
        if not values.get("section_code") and values.get("title"):
            values["section_code"] = _derived_section_code(str(values["title"]))
        return values

    _normalize_text = field_validator(
        "section_code",
        "title",
        "requirement_text",
        mode="before",
    )(_strip_text)

    @model_validator(mode="after")
    def validate_required_text(self) -> "TemplateSectionRequest":
        """Reject legacy or canonical sections missing required text."""
        if not self.section_code:
            raise ValueError("Section code is required.")
        if not self.title:
            raise ValueError("Section name is required.")
        if not self.requirement_text:
            raise ValueError("Section description is required.")
        return self


class TemplateCreateRequest(BaseModel):
    """Validate a canonical or legacy compliance-template payload."""

    name: str = Field(min_length=1, max_length=200)
    version: str = Field(default="unspecified", min_length=1, max_length=50)
    description: str = Field(default="")
    governing_body: GoverningBody | None = None
    framework: str | None = Field(default=None, max_length=255)
    sections: list[TemplateSectionRequest] = Field(min_length=1)

    @model_validator(mode="before")
    @classmethod
    def normalize_legacy_fields(cls, data: object) -> object:
        """Translate a legacy framework label to the canonical body field."""
        if not isinstance(data, Mapping):
            return data

        values = dict(data)
        framework = values.get("framework")
        if isinstance(framework, str):
            values["framework"] = framework.strip()
            if not values.get("governing_body"):
                values["governing_body"] = _governing_body_from_framework(framework)
        return values

    _normalize_text = field_validator(
        "name",
        "version",
        "description",
        mode="before",
    )(_strip_text)

    @model_validator(mode="after")
    def validate_governing_body(self) -> "TemplateCreateRequest":
        """Require a supported canonical governing body or recognizable framework."""
        if self.governing_body is None:
            raise ValueError(
                "Provide governing_body or a framework beginning with FDA, EMA, EU GMP, WHO, or ICH."
            )
        return self


class TemplateUpdateRequest(TemplateCreateRequest):
    """Validate replacement values for an existing compliance template."""


class TemplateSectionResponse(BaseModel):
    """Return one normative section with canonical and legacy response names."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    section_code: str
    title: str
    requirement_text: str
    mandatory: bool
    order_index: int

    @computed_field
    @property
    def section_name(self) -> str:
        """Expose the legacy section name as a response alias."""
        return self.title

    @computed_field
    @property
    def description(self) -> str:
        """Expose the legacy section description as a response alias."""
        return self.requirement_text

    @computed_field
    @property
    def is_mandatory(self) -> bool:
        """Expose the legacy mandatory flag as a response alias."""
        return self.mandatory


class TemplateResponse(BaseModel):
    """Return a template with canonical and legacy response names."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    name: str
    version: str
    description: str
    governing_body: GoverningBody
    sections: list[TemplateSectionResponse]
    created_at: datetime
    updated_at: datetime

    @computed_field
    @property
    def framework(self) -> str:
        """Expose the canonical governing body as the legacy framework label."""
        return self.governing_body


class TemplateSummaryResponse(BaseModel):
    """Return template metadata with a legacy framework alias."""

    id: UUID
    name: str
    version: str
    description: str
    governing_body: GoverningBody
    section_count: int = Field(ge=0)
    created_at: datetime
    updated_at: datetime

    @computed_field
    @property
    def framework(self) -> str:
        """Expose the canonical governing body as the legacy framework label."""
        return self.governing_body


class TemplateCollectionResponse(BaseModel):
    """Return a paginated compliance-template collection."""

    items: list[TemplateSummaryResponse]
    page: int = Field(ge=1)
    limit: int = Field(ge=1, le=100)
    total: int = Field(ge=0)
