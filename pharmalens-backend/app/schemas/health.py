"""Health-check response schema."""

from pydantic import BaseModel


class HealthResponse(BaseModel):
    """Describe the availability of the FastAPI process."""

    status: str
    service: str
