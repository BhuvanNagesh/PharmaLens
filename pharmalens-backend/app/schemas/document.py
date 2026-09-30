"""Pydantic schemas for document ingestion and retrieval endpoints."""

from __future__ import annotations

from datetime import datetime
from typing import Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


DocumentFileType = Literal["pdf", "docx"]
MAX_DOCUMENT_SIZE_BYTES = 300 * 1024 * 1024


class DocumentSummaryResponse(BaseModel):
    """Return document metadata for collection responses."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    filename: str
    file_type: DocumentFileType
    file_size_bytes: int = Field(ge=0, le=MAX_DOCUMENT_SIZE_BYTES)
    storage_path: str | None
    uploaded_at: datetime


class DocumentResponse(DocumentSummaryResponse):
    """Return document metadata and extracted text."""

    extracted_text: str
    created_at: datetime
    updated_at: datetime


class DocumentCollectionResponse(BaseModel):
    """Return a paginated document collection."""

    items: list[DocumentSummaryResponse]
    page: int = Field(ge=1)
    limit: int = Field(ge=1, le=100)
    total: int = Field(ge=0)
