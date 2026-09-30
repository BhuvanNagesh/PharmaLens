"""Document upload, retrieval, and deletion endpoints."""

from __future__ import annotations

import asyncio
import io
import logging
from pathlib import Path
from uuid import UUID, uuid4
from zipfile import is_zipfile

from fastapi import APIRouter, Depends, File, HTTPException, Query, UploadFile, status
from sqlalchemy import func, select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.models.audit import AuditLog
from app.models.document import Document
from app.schemas.document import (
    DocumentCollectionResponse,
    DocumentResponse,
    DocumentSummaryResponse,
    MAX_DOCUMENT_SIZE_BYTES,
)
from app.services.document_processor import DocumentProcessingError, extract_text
from app.services.storage_service import StorageService, StorageServiceError


logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/documents", tags=["documents"])

SUPPORTED_CONTENT_TYPES: dict[str, str] = {
    "pdf": "application/pdf",
    "docx": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
}
UNSUPPORTED_FILE_MESSAGE = (
    "Unsupported file type. Only PDF and DOCX files are accepted"
)
MAX_FILENAME_LENGTH = 255


def _file_type_from_upload(file: UploadFile) -> str:
    """Validate the uploaded filename and content type, then return its extension."""
    filename = (file.filename or "").strip()
    if not filename:
        raise HTTPException(status_code=400, detail="No file uploaded")
    if len(filename) > MAX_FILENAME_LENGTH:
        raise HTTPException(
            status_code=400,
            detail="Filename must be 255 characters or fewer",
        )
    if any(ord(character) < 32 for character in filename):
        raise HTTPException(
            status_code=400,
            detail="Filename contains unsupported control characters",
        )

    file_type = Path(filename).suffix.lower().lstrip(".")
    expected_content_type = SUPPORTED_CONTENT_TYPES.get(file_type)
    content_type = (file.content_type or "").strip().lower()
    if expected_content_type is None or content_type != expected_content_type:
        raise HTTPException(status_code=400, detail=UNSUPPORTED_FILE_MESSAGE)
    return file_type


async def _read_upload(file: UploadFile) -> tuple[str, bytes]:
    """Validate size and read one supported upload into memory."""
    file_type = _file_type_from_upload(file)
    if file.size is not None and file.size > MAX_DOCUMENT_SIZE_BYTES:
        raise HTTPException(
            status_code=413,
            detail="File size exceeds 300MB limit",
        )

    file_bytes = await file.read(MAX_DOCUMENT_SIZE_BYTES + 1)
    if len(file_bytes) > MAX_DOCUMENT_SIZE_BYTES:
        raise HTTPException(
            status_code=413,
            detail="File size exceeds 300MB limit",
        )
    if not file_bytes:
        raise HTTPException(status_code=400, detail="The uploaded file is empty")
    if file_type == "pdf" and b"%PDF-" not in file_bytes[:1024]:
        raise HTTPException(
            status_code=400,
            detail="The uploaded file content does not match a PDF document",
        )
    if file_type == "docx" and not is_zipfile(io.BytesIO(file_bytes)):
        raise HTTPException(
            status_code=400,
            detail="The uploaded file content does not match a DOCX document",
        )
    return file_type, file_bytes


async def _cleanup_storage_file(storage: StorageService, storage_path: str) -> None:
    """Best-effort cleanup for a file uploaded before a database failure."""
    try:
        await storage.delete_file(storage_path)
    except StorageServiceError:
        logger.exception("Could not clean up storage path after a database failure.")


@router.post("", response_model=DocumentResponse, status_code=status.HTTP_201_CREATED)
async def upload_document(
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
) -> Document:
    """Extract, store, and persist one PDF or DOCX document."""
    file_type, file_bytes = await _read_upload(file)
    filename = (file.filename or "").strip()
    document_id = uuid4()
    storage_path = f"{document_id}.{file_type}"
    storage: StorageService | None = None
    storage_uploaded = False

    try:
        storage = StorageService()
        extracted_text = await asyncio.to_thread(extract_text, file_bytes, file_type)
        await storage.upload_file(
            file_bytes,
            storage_path,
            SUPPORTED_CONTENT_TYPES[file_type],
        )
        storage_uploaded = True

        document = Document(
            id=document_id,
            filename=filename,
            file_type=file_type,
            file_size_bytes=len(file_bytes),
            storage_path=storage_path,
            extracted_text=extracted_text,
        )
        db.add(document)
        db.add(
            AuditLog(
                entity_type="document",
                entity_id=document_id,
                action="uploaded",
                metadata_json={
                    "filename": filename,
                    "file_type": file_type,
                    "file_size_bytes": len(file_bytes),
                },
            )
        )
        await db.commit()
        return document
    except DocumentProcessingError as error:
        await db.rollback()
        raise HTTPException(
            status_code=400,
            detail="Unable to process this file. The document may be corrupted",
        ) from error
    except StorageServiceError as error:
        await db.rollback()
        logger.error("Document storage failed for filename=%s: %s", filename, error)
        raise HTTPException(
            status_code=500,
            detail="Unable to store the uploaded document",
        ) from error
    except SQLAlchemyError as error:
        await db.rollback()
        if storage_uploaded and storage is not None:
            await _cleanup_storage_file(storage, storage_path)
        logger.exception("Document database persistence failed for filename=%s", filename)
        raise HTTPException(
            status_code=500,
            detail="Internal server error",
        ) from error
    except Exception as error:
        await db.rollback()
        if storage_uploaded and storage is not None:
            await _cleanup_storage_file(storage, storage_path)
        logger.exception("Unexpected document upload failure for filename=%s", filename)
        raise HTTPException(status_code=500, detail="Internal server error") from error
    finally:
        if storage is not None:
            try:
                await storage.close()
            except Exception:
                logger.exception("Could not close the document storage client.")


@router.get("", response_model=DocumentCollectionResponse)
async def list_documents(
    page: int = Query(default=1, ge=1),
    limit: int = Query(default=10, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
) -> DocumentCollectionResponse:
    """Return paginated uploaded-document metadata."""
    total = int(await db.scalar(select(func.count()).select_from(Document)) or 0)
    result = await db.execute(
        select(Document)
        .order_by(Document.uploaded_at.desc(), Document.id.desc())
        .offset((page - 1) * limit)
        .limit(limit)
    )
    documents = result.scalars().all()
    return DocumentCollectionResponse(
        items=[DocumentSummaryResponse.model_validate(document) for document in documents],
        page=page,
        limit=limit,
        total=total,
    )


@router.get("/{document_id}", response_model=DocumentResponse)
async def get_document(
    document_id: UUID,
    db: AsyncSession = Depends(get_db),
) -> Document:
    """Return one document with its extracted text."""
    document = await db.get(Document, document_id)
    if document is None:
        raise HTTPException(status_code=404, detail="Document not found")
    return document


@router.delete(
    "/{document_id}",
    response_model=None,
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_document(
    document_id: UUID,
    db: AsyncSession = Depends(get_db),
) -> None:
    """Delete one document, its storage object, and cascaded analyses."""
    document = await db.get(Document, document_id)
    if document is None:
        raise HTTPException(status_code=404, detail="Document not found")

    storage = StorageService()
    try:
        if document.storage_path:
            await storage.delete_file(document.storage_path)
        db.add(
            AuditLog(
                entity_type="document",
                entity_id=document.id,
                action="deleted",
                metadata_json={"filename": document.filename},
            )
        )
        await db.delete(document)
        await db.commit()
    except StorageServiceError as error:
        await db.rollback()
        logger.error("Document storage deletion failed for id=%s: %s", document_id, error)
        raise HTTPException(
            status_code=500,
            detail="Unable to delete the stored document",
        ) from error
    except SQLAlchemyError as error:
        await db.rollback()
        logger.exception("Document deletion failed for id=%s", document_id)
        raise HTTPException(status_code=500, detail="Internal server error") from error
    finally:
        try:
            await storage.close()
        except Exception:
            logger.exception("Could not close the document storage client.")
