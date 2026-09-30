"""Asynchronous Supabase Storage operations for original regulatory files."""

from __future__ import annotations

from collections.abc import Mapping
from uuid import UUID
from urllib.parse import quote

import httpx

from app.core.config import settings


ALLOWED_CONTENT_TYPES: frozenset[str] = frozenset(
    {
        "application/pdf",
        "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    }
)
MAX_SIGNED_URL_EXPIRY_SECONDS = 604_800


class StorageServiceError(Exception):
    """Indicate that a Supabase Storage operation failed."""


class StorageService:
    """Provide authenticated asynchronous operations for one private bucket."""

    def __init__(
        self,
        supabase_url: str | None = None,
        publishable_key: str | None = None,
        bucket_name: str | None = None,
        client: httpx.AsyncClient | None = None,
    ) -> None:
        """Initialize the service from settings or explicitly supplied test values."""
        resolved_url = (
            settings.supabase_url if supabase_url is None else supabase_url
        ).rstrip("/")
        resolved_key = (
            settings.supabase_key if publishable_key is None else publishable_key
        )
        resolved_bucket = (
            settings.storage_bucket if bucket_name is None else bucket_name
        )

        if not resolved_url or not resolved_key:
            raise StorageServiceError(
                "Supabase Storage is not configured. Set SUPABASE_URL and "
                "SUPABASE_PUBLISHABLE_KEY."
            )
        if not resolved_bucket.strip():
            raise StorageServiceError("STORAGE_BUCKET must not be empty.")
        if "/" in resolved_bucket or "\\" in resolved_bucket:
            raise StorageServiceError("STORAGE_BUCKET must be a single bucket name.")

        self._base_url = resolved_url
        self._bucket_name = resolved_bucket.strip()
        self._headers = {
            "apikey": resolved_key,
            "Authorization": f"Bearer {resolved_key}",
        }
        self._owns_client = client is None
        self._client = client or httpx.AsyncClient(
            timeout=httpx.Timeout(settings.storage_timeout_seconds, connect=10.0)
        )

    async def close(self) -> None:
        """Close the HTTP client when this service created it."""
        if self._owns_client:
            await self._client.aclose()

    @staticmethod
    def build_document_path(document_id: UUID, file_type: str) -> str:
        """Build the canonical bucket path for a document UUID and extension."""
        if not isinstance(file_type, str):
            raise StorageServiceError("Only PDF and DOCX documents can be stored.")
        normalized_file_type = file_type.lower().strip().lstrip(".")
        content_type_by_extension = {
            "pdf": "application/pdf",
            "docx": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        }
        if normalized_file_type not in content_type_by_extension:
            raise StorageServiceError("Only PDF and DOCX documents can be stored.")
        return f"{document_id}.{normalized_file_type}"

    async def upload_file(
        self,
        file_bytes: bytes,
        storage_path: str,
        content_type: str,
        *,
        upsert: bool = False,
    ) -> str:
        """Upload document bytes and return the canonical Supabase Storage path."""
        if not isinstance(file_bytes, bytes) or not file_bytes:
            raise StorageServiceError("The file to upload is empty.")
        if not isinstance(content_type, str) or content_type not in ALLOWED_CONTENT_TYPES:
            raise StorageServiceError("Only PDF and DOCX documents can be stored.")

        path = self._validate_storage_path(storage_path)
        endpoint = self._object_endpoint(path)
        headers = {
            **self._headers,
            "Content-Type": content_type,
            "x-upsert": str(upsert).lower(),
        }

        try:
            response = await self._client.post(
                f"{self._base_url}{endpoint}",
                content=file_bytes,
                headers=headers,
            )
        except httpx.HTTPError as error:
            raise StorageServiceError(
                "Supabase Storage could not be reached while uploading the file."
            ) from error

        self._raise_for_storage_error(response, "upload")
        return path

    async def create_signed_url(
        self,
        storage_path: str,
        expires_in: int = 3_600,
    ) -> str:
        """Create a time-limited signed URL for a private stored document."""
        if (
            isinstance(expires_in, bool)
            or not isinstance(expires_in, int)
            or not 1 <= expires_in <= MAX_SIGNED_URL_EXPIRY_SECONDS
        ):
            raise StorageServiceError(
                "Signed URL expiry must be between 1 second and 7 days."
            )

        path = self._validate_storage_path(storage_path)
        endpoint = self._signed_object_endpoint(path)
        try:
            response = await self._client.post(
                f"{self._base_url}{endpoint}",
                json={"expiresIn": expires_in},
                headers=self._headers,
            )
        except httpx.HTTPError as error:
            raise StorageServiceError(
                "Supabase Storage could not be reached while creating the download URL."
            ) from error

        self._raise_for_storage_error(response, "signed URL creation")
        payload = self._json_mapping(response, "signed URL creation")
        signed_url = payload.get("signedURL") or payload.get("signed_url")
        if not isinstance(signed_url, str) or not signed_url:
            raise StorageServiceError(
                "Supabase Storage returned an invalid signed download URL."
            )
        if signed_url.startswith("/"):
            return f"{self._base_url}{signed_url}"
        return signed_url

    async def download_file(self, storage_path: str) -> bytes:
        """Download stored document bytes through the authenticated Storage API."""
        path = self._validate_storage_path(storage_path)
        try:
            response = await self._client.get(
                f"{self._base_url}{self._object_endpoint(path)}",
                headers=self._headers,
            )
        except httpx.HTTPError as error:
            raise StorageServiceError(
                "Supabase Storage could not be reached while downloading the file."
            ) from error

        self._raise_for_storage_error(response, "download")
        return response.content

    async def delete_file(self, storage_path: str) -> None:
        """Delete one stored document from the configured Supabase bucket."""
        path = self._validate_storage_path(storage_path)
        endpoint = (
            "/storage/v1/object/"
            f"{quote(self._bucket_name, safe='')}"
        )
        try:
            response = await self._client.request(
                "DELETE",
                f"{self._base_url}{endpoint}",
                json={"prefixes": [path]},
                headers=self._headers,
            )
        except httpx.HTTPError as error:
            raise StorageServiceError(
                "Supabase Storage could not be reached while deleting the file."
            ) from error

        self._raise_for_storage_error(response, "deletion")

    def _object_endpoint(self, storage_path: str) -> str:
        """Return the URL path for a bucket object operation."""
        return (
            "/storage/v1/object/"
            f"{quote(self._bucket_name, safe='')}/"
            f"{quote(storage_path, safe='/')}"
        )

    def _signed_object_endpoint(self, storage_path: str) -> str:
        """Return the URL path for a signed bucket-object operation."""
        return (
            "/storage/v1/object/sign/"
            f"{quote(self._bucket_name, safe='')}/"
            f"{quote(storage_path, safe='/')}"
        )

    @staticmethod
    def _validate_storage_path(storage_path: str) -> str:
        """Reject unsafe object paths before sending them to Supabase Storage."""
        if not isinstance(storage_path, str):
            raise StorageServiceError("The storage path is invalid.")
        normalized_path = storage_path.strip().replace("\\", "/")
        path_parts = normalized_path.split("/")
        if (
            not normalized_path
            or normalized_path.startswith("/")
            or any(part in {"", ".", ".."} for part in path_parts)
        ):
            raise StorageServiceError("The storage path is invalid.")
        return normalized_path

    @staticmethod
    def _json_mapping(response: httpx.Response, operation: str) -> Mapping[str, object]:
        """Read a JSON object response or raise a plain storage error."""
        try:
            payload = response.json()
        except ValueError as error:
            raise StorageServiceError(
                f"Supabase Storage returned an invalid response during {operation}."
            ) from error
        if not isinstance(payload, Mapping):
            raise StorageServiceError(
                f"Supabase Storage returned an invalid response during {operation}."
            )
        return payload

    @staticmethod
    def _raise_for_storage_error(response: httpx.Response, operation: str) -> None:
        """Convert an HTTP Storage failure into a safe application exception."""
        if response.is_success:
            return

        if response.status_code in {401, 403}:
            raise StorageServiceError(
                f"Supabase Storage {operation} failed because the request was not authorized."
            )
        if response.status_code == 404:
            raise StorageServiceError(
                f"Supabase Storage {operation} failed because the object or bucket was not found."
            )
        if response.status_code == 413:
            raise StorageServiceError(
                f"Supabase Storage {operation} failed because the file is too large."
            )
        if response.status_code == 429 or response.status_code >= 500:
            raise StorageServiceError(
                f"Supabase Storage {operation} failed because the Storage service is unavailable."
            )

        detail = "unknown storage error"
        try:
            payload = response.json()
            if isinstance(payload, Mapping):
                detail = str(
                    payload.get("message")
                    or payload.get("error")
                    or payload.get("error_description")
                    or detail
                )
            elif response.text:
                detail = response.text
        except ValueError:
            if response.text:
                detail = response.text

        if "row-level security" in detail.lower():
            detail = (
                "Storage object permissions are not configured for the application "
                "bucket."
            )
        safe_detail = detail.replace("\r", " ").replace("\n", " ")[:300]
        raise StorageServiceError(
            f"Supabase Storage {operation} failed with HTTP {response.status_code}: "
            f"{safe_detail}"
        )
