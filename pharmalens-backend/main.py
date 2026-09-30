"""FastAPI application entry point for PharmaLens."""

from __future__ import annotations

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy.exc import SQLAlchemyError

from app.api.analyses import router as analyses_router
from app.api.documents import router as documents_router
from app.api.templates import router as templates_router
from app.core.config import settings
from app.core.database import dispose_database
from app.schemas.health import HealthResponse
from app.services.analysis_service import (
    recover_interrupted_analyses,
    shutdown_analysis_tasks,
)


logging.basicConfig(
    level=getattr(logging, settings.log_level.upper(), logging.INFO),
    format="%(asctime)s %(levelname)s %(name)s %(message)s",
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(_: FastAPI):
    """Dispose the SQLAlchemy connection pool when the process stops."""
    await recover_interrupted_analyses()
    yield
    await shutdown_analysis_tasks()
    await dispose_database()


app = FastAPI(
    title="PharmaLens API",
    description="AI-powered pharmaceutical regulatory compliance backend.",
    version="0.1.0",
    lifespan=lifespan,
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_credentials=False,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["Content-Type", "Accept"],
)


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Return a safe JSON response for unexpected server errors."""
    logger.exception("Unhandled exception while handling %s %s", request.method, request.url.path)
    return JSONResponse(status_code=500, content={"detail": "Internal server error"})


@app.exception_handler(SQLAlchemyError)
async def database_exception_handler(
    request: Request,
    exc: SQLAlchemyError,
) -> JSONResponse:
    """Return a safe response for unexpected database failures."""
    logger.exception(
        "Database error while handling %s %s",
        request.method,
        request.url.path,
        exc_info=(type(exc), exc, exc.__traceback__),
    )
    return JSONResponse(status_code=500, content={"detail": "Internal server error"})


@app.get("/api/health", response_model=HealthResponse, tags=["health"])
async def health_check() -> HealthResponse:
    """Return the process health status."""
    return HealthResponse(status="ok", service="pharmalens-backend")


app.include_router(documents_router)
app.include_router(templates_router)
app.include_router(analyses_router)
