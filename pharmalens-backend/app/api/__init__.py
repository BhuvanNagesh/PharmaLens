"""FastAPI routers for the PharmaLens backend."""

from app.api.analyses import router as analyses_router
from app.api.documents import router as documents_router
from app.api.templates import router as templates_router

__all__ = ["analyses_router", "documents_router", "templates_router"]
