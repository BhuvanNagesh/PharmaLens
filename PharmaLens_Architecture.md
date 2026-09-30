# PharmaLens — Architecture Document

> **Project:** PharmaLens — AI-Powered Regulatory Compliance Copilot  
> **Author:** Bhuvan Nagesh  
> **Created:** 29-09-2026  
> **Status:** Pre-Implementation  

---

## 1. System Overview

PharmaLens is a **full-stack AI-powered SaaS application** that enables pharmaceutical/life-sciences quality teams to upload regulatory documents (SOPs, Batch Manufacturing Records, Deviation Reports) and receive **automated compliance gap analysis** powered by a LangGraph multi-agent AI pipeline.

The system consists of two independently deployable units — a **Python FastAPI backend** and a **React Vite frontend** — connected via REST APIs. Supabase Docker provides both PostgreSQL and Storage for local development and self-hosted deployment.

---

## 2. Tech Stack

### Backend

| Layer | Technology | Version | Purpose |
|-------|-----------|---------|---------|
| **Runtime** | Python | 3.11+ | Primary language |
| **Web Framework** | FastAPI | 0.115.x | Async REST API server |
| **ASGI Server** | Uvicorn | 0.30.x | Production-grade ASGI server |
| **ORM** | SQLAlchemy | 2.0.x | Async ORM with PostgreSQL |
| **Migrations** | Alembic | 1.14.x | Database schema migrations |
| **Database** | Supabase PostgreSQL | — | Supabase Docker/CLI stack, connected via `asyncpg` |
| **DB Driver** | asyncpg | 0.30.x | Async PostgreSQL driver for SQLAlchemy |
| **File Storage** | Supabase Storage | — | Uploaded document file storage (PDFs/DOCX) |
| **AI Orchestration** | LangGraph | 0.4.x | Multi-agent stateful pipeline |
| **AI Core** | LangChain Core | 0.3.x | LLM abstraction layer |
| **LLM Provider** | Google Gemini (primary) / OpenAI GPT (fallback) | — | Generative AI inference |
| **LLM Bindings** | langchain-google-genai / langchain-openai | 2.1.x / 0.3.x | LLM API integration |
| **PDF Extraction** | PyPDF2 | 3.0.x | Extract text from PDF documents |
| **PDF Fallback** | pdfplumber | 0.11.x | Fallback PDF extraction for complex layouts |
| **Optional Vision Parsing** | Dolphin-v2 | External optional runtime | Layout-aware parsing for scanned, photographed, and table-heavy PDFs |
| **DOCX Extraction** | python-docx | 1.1.x | Extract text from DOCX documents |
| **Validation** | Pydantic | 2.10.x | Request/response schema validation |
| **File Upload** | python-multipart | 0.0.x | Multipart form data parsing |
| **Environment** | python-dotenv | 1.1.x | `.env` file loading |
| **HTTP Client** | httpx | 0.28.x | Async HTTP client (for Supabase Storage API) |

### Frontend

| Layer | Technology | Version | Purpose |
|-------|-----------|---------|---------|
| **Runtime** | Node.js | 18+ | JavaScript runtime |
| **Framework** | React | 18.x | UI component library |
| **Build Tool** | Vite | 5.x | Dev server and bundler |
| **Routing** | React Router | 6.x | Client-side SPA routing |
| **HTTP Client** | Axios | 1.7.x | REST API communication |
| **Styling** | Vanilla CSS | — | Global styles + CSS custom properties (design tokens) |
| **Icons** | Lucide React | latest | Consistent icon set |

### Infrastructure

| Layer | Technology | Purpose |
|-------|-----------|---------|
| **Database** | Supabase Docker stack | Same database and storage platform locally and in deployment |
| **File Storage** | Supabase Storage | Document file persistence (PDF/DOCX originals) |
| **Backend Hosting** | Render / Railway (optional) | Containerized FastAPI deployment |
| **Frontend Hosting** | Vercel / Render (optional) | Static React SPA deployment |
| **Containerization** | Docker + Docker Compose | Local development environment |

### Why Use Self-Hosted Supabase Docker

1. **No managed free-tier quota during development** — Database and files use Docker volumes on the host disk.
2. **One platform** — Supabase Docker provides PostgreSQL, Storage, API, and Studio together.
3. **Deployment parity** — The same Supabase Docker stack runs locally and on a Docker-capable deployment host.
4. **Persistent storage** — Database and Storage volumes are explicitly mounted and backed up.
5. **No provider lock-in for the application layer** — The FastAPI app connects through standard PostgreSQL and Supabase Storage APIs.

### 2.1 Supabase Docker Environment

The backend uses one Supabase environment configured entirely through `.env`:

```env
SUPABASE_DB_URL=postgresql+asyncpg://postgres:postgres@127.0.0.1:54322/postgres
SUPABASE_URL=http://127.0.0.1:54321
SUPABASE_PUBLISHABLE_KEY=key-from-supabase-start
STORAGE_BUCKET=pharmalens-docs
STORAGE_TIMEOUT_SECONDS=120
LLM_MAX_ATTEMPTS=2
```

For a Docker deployment host, replace the local hostnames with the Supabase service names and use persistent Docker volumes:

```env
SUPABASE_DB_URL=postgresql+asyncpg://postgres:password@supabase-db:5432/postgres
SUPABASE_URL=http://supabase-kong:8000
```

The application never configures or connects to a standalone PostgreSQL installation. Supabase Cloud may be used later as an optional managed alternative, but it is not required by the canonical architecture.

---

## 3. System Architecture

```
┌─────────────────────────────────────────────────────────────────────────┐
│                              CLIENT LAYER                               │
│                                                                         │
│   ┌──────────────────────────────────────────────────────────────────┐  │
│   │                   React SPA (Vite + React 18)                    │  │
│   │                                                                  │  │
│   │  ┌──────────┐  ┌──────────────┐  ┌───────────┐  ┌───────────┐  │  │
│   │  │Dashboard │  │Upload &      │  │ Analysis  │  │ History   │  │  │
│   │  │Page      │  │Analyze Page  │  │ Report    │  │ Page      │  │  │
│   │  └──────────┘  └──────────────┘  └───────────┘  └───────────┘  │  │
│   │                                                                  │  │
│   │  services/api.js ──── Axios HTTP Client ────────────────────┐   │  │
│   └──────────────────────────────────────────────────────────────┘   │  │
│                                        │                              │  │
│                                   REST API                            │  │
│                                   (JSON)                              │  │
└────────────────────────────────────────┼────────────────────────────────┘
                                         │
┌────────────────────────────────────────┼────────────────────────────────┐
│                              SERVER LAYER                               │
│                                                                         │
│   ┌────────────────────────────────────▼─────────────────────────────┐  │
│   │                    FastAPI Application                            │  │
│   │                                                                  │  │
│   │  ┌─── Middleware ────────────────────────────────────────────┐   │  │
│   │  │  CORS · Request Logging · Error Handler                   │   │  │
│   │  └──────────────────────────────────────────────────────────┘   │  │
│   │                                                                  │  │
│   │  ┌─── API Routers ──────────────────────────────────────────┐   │  │
│   │  │                                                           │   │  │
│   │  │  /api/documents   ←── Document Upload, List, Get, Delete  │   │  │
│   │  │  /api/templates   ←── Compliance Template CRUD            │   │  │
│   │  │  /api/analyses    ←── Trigger Analysis, Get Report, List  │   │  │
│   │  │                                                           │   │  │
│   │  └──────────────┬────────────────────────────────────────────┘   │  │
│   │                 │                                                │  │
│   │  ┌──────────────▼───────────────────────────────────────────┐   │  │
│   │  │              Service Layer                                │   │  │
│   │  │                                                           │   │  │
│   │  │  document_processor.py ←── PDF/DOCX text extraction       │   │  │
│   │  │  analysis_service.py   ←── Orchestrates LangGraph pipeline│   │  │
│   │  │  audit_service.py      ←── Audit trail logging            │   │  │
│   │  │  storage_service.py    ←── Supabase Storage upload/download│  │  │
│   │  │                                                           │   │  │
│   │  └──────────────┬────────────────────────────────────────────┘   │  │
│   │                 │                                                │  │
│   │  ┌──────────────▼───────────────────────────────────────────┐   │  │
│   │  │         LangGraph Multi-Agent Pipeline                    │   │  │
│   │  │                                                           │   │  │
│   │  │  Agent 1: Document Parser & Section Extractor             │   │  │
│   │  │      ↓                                                    │   │  │
│   │  │  Agent 2: Regulatory Framework Mapper                     │   │  │
│   │  │      ↓                                                    │   │  │
│   │  │  Agent 3: Gap Analyzer & Risk Classifier                  │   │  │
│   │  │      ↓                                                    │   │  │
│   │  │  Agent 4: Corrective Action Recommender                   │   │  │
│   │  │                                                           │   │  │
│   │  └──────────────────────────────────────────────────────────┘   │  │
│   │                                                                  │  │
│   │  ┌─── Data Layer ───────────────────────────────────────────┐   │  │
│   │  │  SQLAlchemy Async ORM · Alembic Migrations               │   │  │
│   │  └──────────────┬────────────────────────────────────────────┘   │  │
│   └─────────────────┼────────────────────────────────────────────────┘  │
│                     │                                                    │
└─────────────────────┼────────────────────────────────────────────────────┘
                      │
┌─────────────────────┼────────────────────────────────────────────────────┐
│                     │          DATA LAYER (Supabase)                      │
│                     │                                                    │
│   ┌─────────────────▼──────────────┐   ┌─────────────────────────────┐  │
│   │ Supabase PostgreSQL via Docker  │   │     Supabase Storage        │  │
│   │                                │   │                             │  │
│   │  documents                     │   │  pharmalens-docs/           │  │
│   │  compliance_templates          │   │    ├── <uuid>.pdf           │  │
│   │  template_sections             │   │    └── <uuid>.docx          │  │
│   │  analyses                      │   │                             │  │
│   │  analysis_gaps                 │   │  (Original uploaded files)  │  │
│   │  corrective_actions            │   │                             │  │
│   │  audit_logs                    │   └─────────────────────────────┘  │
│   │                                │                                    │
│   └────────────────────────────────┘                                    │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## 4. Application Flow

### 4.1 Document Upload Flow

```
User drags PDF/DOCX into FileDropZone
    │
    ▼
React validates file type (only .pdf / .docx) and size (≤ 300 MB)
    │
    ▼
POST /api/documents (multipart/form-data)
    │
    ▼
FastAPI receives file → document_processor.py:
    ├── If PDF: native PyPDF2 extraction with pdfplumber fallback
    │          └── In auto mode, an empty/short result can use optional Dolphin-v2
    │              layout and element parsing for scanned or photographed pages
    └── If DOCX: python-docx extracts text from all paragraphs
    │
    ▼
storage_service.py uploads original file to Supabase Storage
    bucket: "pharmalens-docs"
    path: "<document_uuid>.<extension>"
    │
    ▼
SQLAlchemy inserts into `documents` table:
    id, filename, file_type, file_size_bytes, extracted_text,
    storage_path, uploaded_at
    │
    ▼
Audit log entry: { entity_type: "document", action: "uploaded" }
    │
    ▼
Returns 201: { id, filename, file_type, file_size_bytes, uploaded_at }
```

### 4.2 Compliance Analysis Flow

```
User selects template from dropdown → clicks "Analyze"
    │
    ▼
POST /api/analyses { document_id, template_id }
    │
    ▼
FastAPI validates:
    ├── document_id exists in `documents` table     → 404 if not
    └── template_id exists in `compliance_templates` → 404 if not
    │
    ▼
Creates `analyses` record with status = "processing"
    │
    ▼
Returns 202: { analysis_id, status: "processing" }
    │
    ▼
Async: analysis_service.py invokes LangGraph pipeline
    │
    ▼
┌─────────────────────────────────────────────────────────┐
│              LangGraph StateGraph Execution              │
│                                                          │
│  Input State:                                            │
│    document_text = <extracted text from DB>               │
│    template_sections = <loaded from template_sections>   │
│                                                          │
│  Node 1: document_parser_agent                           │
│    → LLM call: "Extract and label all document sections" │
│    → Output: document_sections[]                         │
│                                                          │
│  Node 2: regulatory_mapper_agent                         │
│    → LLM call: "Map document sections to template"       │
│    → Output: section_mapping[]                           │
│                                                          │
│  Node 3: gap_analyzer_agent                              │
│    → LLM call: "Identify gaps, classify severity"        │
│    → Output: gaps[] (critical / major / minor)           │
│                                                          │
│  Node 4: corrective_action_agent                         │
│    → LLM call: "Generate corrective actions per gap"     │
│    → Output: corrective_actions[]                        │
│                                                          │
│  Deterministic score calculator                          │
│    → Applies critical/major/minor penalty weights         │
│    → Output: compliance_score (0–100)                    │
│                                                          │
└─────────────────────────────────────────────────────────┘
    │
    ▼
Pipeline output persisted:
    ├── analysis_gaps[] → `analysis_gaps` table
    ├── corrective_actions[] → `corrective_actions` table
    └── analyses.status → "completed"
        analyses.total_gaps, critical_gaps, major_gaps, minor_gaps
    │
    ▼
Audit log entry: { entity_type: "analysis", action: "analysis_completed" }
```

The background worker opens its own `AsyncSessionLocal` session and never reuses the request session after the `202 Accepted` response. Completion persists the score, severity counts, gaps, corrective actions, summary, timestamp, and `analysis_completed` audit event in one transaction. Pipeline exceptions are converted into a bounded `failed` analysis record with an `analysis_failed` audit event. Application shutdown cancels outstanding workers before disposing the database pool.

### 4.3 Report Retrieval Flow

```
React polls GET /api/analyses/:id every 3 seconds
    │
    ├── status == "processing" → show spinner "AI agents analyzing..."
    ├── status == "failed"     → show error banner with retry option
    └── status == "completed"  → auto-navigate to Analysis Report page
            │
            ▼
        Report page calls GET /api/analyses/:id
            │
            ▼
        Backend returns full analysis with nested:
            ├── document metadata
            ├── template metadata
            ├── summary (total_gaps, critical, major, minor)
            ├── gaps[] with severity, gap_type, description
            │   └── corrective_actions[] per gap
            └── audit trail
```

### 4.4 Frontend Page Navigation Flow

```
http://localhost:5173/
    │
    ├── /              → Dashboard
    │                     GET /api/documents (count)
    │                     GET /api/analyses (recent, limit=5)
    │
    ├── /upload        → Upload & Analyze
    │                     GET /api/templates (dropdown population)
    │                     POST /api/documents (file upload)
    │                     POST /api/analyses (trigger)
    │                     GET /api/analyses/:id (polling)
    │
    ├── /analysis/:id  → Analysis Report
    │                     GET /api/analyses/:id (full report)
    │
    └── /history       → Analysis History
                          GET /api/analyses (all, paginated)
```

---

## 5. LangGraph Pipeline Architecture

### 5.1 State Schema

```python
from typing import TypedDict

class ComplianceState(TypedDict):
    # Input
    document_text: str                    # Raw extracted text
    template_sections: list[dict]         # Required sections from DB

    # Agent 1 Output
    document_sections: list[dict]         # { section_title, section_content }

    # Agent 2 Output
    section_mapping: list[dict]           # { template_section, matched_section, confidence }

    # Agent 3 Output
    gaps: list[dict]                      # { section_name, severity, gap_type, description }

    # Agent 4 Output
    corrective_actions: list[dict]        # { gap_section, recommendation, priority }

    # Metadata
    metadata: dict                        # document_id, template_id, timestamps
```

### 5.2 Graph Definition

```
START
  │
  ▼
┌─────────────────────┐
│ document_parser      │  Agent 1
│ (extract sections)   │
└─────────┬───────────┘
          │
          ▼
┌─────────────────────┐
│ regulatory_mapper    │  Agent 2
│ (map to template)    │
└─────────┬───────────┘
          │
          ▼
┌─────────────────────┐
│ gap_analyzer         │  Agent 3
│ (find gaps + severity│
└─────────┬───────────┘
          │
          ▼
┌─────────────────────┐
│ corrective_advisor   │  Agent 4
│ (recommendations)    │
└─────────┬───────────┘
          │
          ▼
        END
```

### 5.3 LLM Configuration

| Setting | Value |
|---------|-------|
| **Primary Model** | `gemini-1.5-flash` (Google) |
| **Fallback Model** | `gpt-4o-mini` (OpenAI) |
| **Temperature** | 0.1 (low — deterministic, structured output) |
| **Response Format** | JSON mode (structured output) |
| **Max Retries** | 2 per agent (with clarification prompt on retry) |
| **Timeout** | 30 seconds per agent call |
| **Token Budget** | ~4,000 input tokens per agent call (chunking if exceeded) |

---

## 6. Database Schema (Supabase PostgreSQL via Docker)

### 6.1 Entity Relationship Diagram

```
┌──────────────────────┐       ┌─────────────────────────┐
│     documents        │       │  compliance_templates    │
│──────────────────────│       │─────────────────────────│
│ id (PK, UUID)        │       │ id (PK, UUID)           │
│ filename             │       │ name                    │
│ file_type            │       │ description             │
│ file_size_bytes      │       │ framework               │
│ extracted_text       │       │ created_at              │
│ storage_path         │       └────────┬────────────────┘
│ uploaded_at          │                │ 1:N
└────────┬─────────────┘                │
         │ 1:N                 ┌────────▼────────────────┐
         │                     │   template_sections     │
┌────────▼─────────────┐       │─────────────────────────│
│      analyses        │       │ id (PK, UUID)           │
│──────────────────────│       │ template_id (FK)        │
│ id (PK, UUID)        │       │ section_name            │
│ document_id (FK)     │───┐   │ description             │
│ template_id (FK)     │───┘   │ is_mandatory            │
│ status               │       │ order_index             │
│ total_gaps           │       └─────────────────────────┘
│ critical_gaps        │
│ major_gaps           │
│ minor_gaps           │
│ started_at           │
│ completed_at         │
│ created_at           │
└────────┬─────────────┘
         │ 1:N
┌────────▼─────────────┐
│    analysis_gaps     │
│──────────────────────│
│ id (PK, UUID)        │
│ analysis_id (FK)     │
│ section_name         │
│ severity             │
│ gap_type             │
│ description          │
│ document_excerpt     │
└────────┬─────────────┘
         │ 1:N
┌────────▼─────────────┐
│  corrective_actions  │
│──────────────────────│
│ id (PK, UUID)        │
│ gap_id (FK)          │
│ recommendation       │
│ priority             │
└──────────────────────┘

┌──────────────────────┐
│     audit_logs       │
│──────────────────────│
│ id (PK, UUID)        │
│ entity_type          │
│ entity_id            │
│ action               │
│ details (JSONB)      │
│ performed_at         │
└──────────────────────┘
```

### 6.2 Index Strategy

| Table | Index Columns | Type | Purpose |
|-------|--------------|------|---------|
| `analyses` | `document_id` | B-tree | Filter analyses by document |
| `analyses` | `template_id` | B-tree | Filter analyses by template |
| `analyses` | `status` | B-tree | Filter by processing status |
| `analysis_gaps` | `analysis_id` | B-tree | Load gaps for a specific analysis |
| `analysis_gaps` | `severity` | B-tree | Filter/count gaps by severity |
| `corrective_actions` | `gap_id` | B-tree | Load actions for a specific gap |
| `audit_logs` | `(entity_type, entity_id)` | Composite B-tree | Audit trail lookup |
| `audit_logs` | `performed_at` | B-tree | Chronological audit queries |

### 6.3 Public-Schema Security

All application tables and the Alembic bookkeeping table are exposed in the Supabase `public` schema, so migration `002_enable_public_rls` enables PostgreSQL row-level security on `alembic_version`, `documents`, `compliance_templates`, `template_sections`, `analyses`, `analysis_gaps`, `corrective_actions`, and `audit_logs`. No public data policies are created for the unauthenticated v1 API; this makes direct PostgREST access deny-by-default while the trusted FastAPI database connection continues to perform server-side ORM operations. Storage remains separately protected by bucket-scoped policies.

---

## 7. Folder & File Structure

### 7.1 Backend — `pharmalens-backend/`

```
pharmalens-backend/
│
├── main.py                              # FastAPI app entry point
│                                        #   - App creation, CORS middleware
│                                        #   - Router registration
│                                        #   - Lifespan event (DB init, Supabase client)
│
├── config.py                            # Configuration & environment variables
│                                        #   - SUPABASE_URL, SUPABASE_PUBLISHABLE_KEY
│                                        #   - SUPABASE_DB_URL connection string
│                                        #   - GOOGLE_API_KEY / OPENAI_API_KEY
│                                        #   - STORAGE_BUCKET name
│                                        #   - CORS_ORIGINS
│
├── requirements.txt                     # Python dependencies (pinned versions)
├── alembic.ini                          # Alembic configuration
├── .env                                 # Environment variables (git-ignored)
├── .gitignore                           # Git ignore rules
│
├── alembic/                             # Database migrations
│   ├── env.py                           # Alembic environment config
│   └── versions/                        # Migration scripts
│       ├── 001_initial_schema.py        # Initial table creation
│       └── 002_enable_public_rls.py     # Deny-by-default public-table RLS
│
├── routers/                             # API route handlers
│   ├── __init__.py
│   ├── documents.py                     # POST /api/documents (upload)
│   │                                    # GET  /api/documents (list)
│   │                                    # GET  /api/documents/:id (detail)
│   │                                    # DELETE /api/documents/:id
│   │
│   ├── templates.py                     # POST /api/templates (create)
│   │                                    # GET  /api/templates (list)
│   │                                    # GET  /api/templates/:id (detail)
│   │                                    # PUT  /api/templates/:id (update)
│   │                                    # DELETE /api/templates/:id
│   │
│   └── analyses.py                      # POST /api/analyses (trigger)
│                                        # GET  /api/analyses (list/filter)
│                                        # GET  /api/analyses/:id (full report)
│
├── models/                              # SQLAlchemy ORM models
│   ├── __init__.py
│   ├── database.py                      # AsyncEngine, AsyncSession factory, Base
│   │                                    #   - Connection string from SUPABASE_DB_URL
│   │                                    #   - async get_db() dependency
│   │
│   ├── document.py                      # Document model
│   ├── template.py                      # ComplianceTemplate + TemplateSection models
│   ├── analysis.py                      # Analysis, AnalysisGap, CorrectiveAction models
│   └── audit_log.py                     # AuditLog model
│
├── schemas/                             # Pydantic request/response schemas
│   ├── __init__.py
│   ├── document.py                      # DocumentCreate, DocumentResponse, DocumentList
│   ├── template.py                      # TemplateCreate, TemplateSectionCreate,
│   │                                    # TemplateResponse, TemplateListResponse
│   └── analysis.py                      # AnalysisCreate, AnalysisResponse,
│                                        # GapResponse, CorrectiveActionResponse,
│                                        # AnalysisReportResponse
│
├── services/                            # Business logic layer
│   ├── __init__.py
│   ├── document_processor.py            # PDF text extraction (PyPDF2 + pdfplumber fallback)
│   │                                    # DOCX text extraction (python-docx)
│   │                                    # optional Dolphin-v2 provider for PDFs
│   ├── dolphin_parser.py                # Lazy-loaded optional Dolphin-v2 adapter
│   │                                    # two-stage layout + element extraction
│   │
│   ├── storage_service.py               # Supabase Storage operations
│   │                                    #   - upload_file(bucket, path, file_bytes)
│   │                                    #   - get_public_url(bucket, path)
│   │                                    #   - delete_file(bucket, path)
│   │
│   ├── analysis_service.py              # Orchestrates LangGraph pipeline
│   │                                    #   - deterministic score calculation
│   │                                    #   - load document text + template sections
│   │                                    #   - invoke compliance_pipeline
│   │                                    #   - persist results to DB
│   │                                    #   - update analysis status
│   │
│   └── audit_service.py                 # Audit trail logging helper
│                                        #   - log_action(entity_type, entity_id, action, details)
│
├── agents/                              # LangGraph AI agents
│   ├── __init__.py
│   ├── compliance_pipeline.py           # LangGraph StateGraph definition
│   │                                    #   - ComplianceState TypedDict
│   │                                    #   - Graph: START → parser → mapper → analyzer → advisor → END
│   │                                    #   - compile() and invoke()
│   │
│   ├── document_parser_agent.py         # Agent 1: Extract + label sections from document text
│   ├── regulatory_mapper_agent.py       # Agent 2: Map document sections to template sections
│   ├── gap_analyzer_agent.py            # Agent 3: Identify gaps + classify severity
│   ├── corrective_action_agent.py       # Agent 4: Generate corrective action recommendations
│   └── llm_config.py                    # LLM initialization (Gemini primary, OpenAI fallback)
│                                        #   - get_llm() → returns configured ChatModel
│
└── utils/                               # Utility functions
    ├── __init__.py
    └── logger.py                        # Structured logging (Python logging module)
```

### 7.2 Frontend — `pharmalens-frontend/`

```
pharmalens-frontend/
│
├── public/
│   └── index.html                       # HTML entry point
│
├── src/
│   ├── main.jsx                         # React entry point (ReactDOM.createRoot)
│   ├── App.jsx                          # Root component: React Router setup + layout
│   ├── App.css                          # Global styles + CSS custom properties (design tokens)
│   │
│   ├── components/
│   │   ├── layout/
│   │   │   ├── Navbar.jsx               # Top navigation bar with page links
│   │   │   └── PageContainer.jsx        # Wrapper with padding + max-width centering
│   │   │
│   │   ├── common/
│   │   │   ├── StatCard.jsx             # Reusable stat display card (count + label + icon)
│   │   │   ├── SeverityBadge.jsx        # Critical (red) / Major (orange) / Minor (yellow) badge
│   │   │   ├── LoadingSpinner.jsx       # Full-page or inline loading spinner
│   │   │   ├── EmptyState.jsx           # Empty state illustration + message
│   │   │   └── ErrorBanner.jsx          # Error message banner with retry button
│   │   │
│   │   ├── upload/
│   │   │   ├── FileDropZone.jsx         # Drag-and-drop file upload with validation
│   │   │   ├── TemplateSelector.jsx     # Dropdown populated from GET /api/templates
│   │   │   └── AnalysisProgress.jsx     # Polling-based progress indicator (spinner + status)
│   │   │
│   │   ├── report/
│   │   │   ├── GapSummaryCard.jsx       # Total/Critical/Major/Minor gap counts with badges
│   │   │   ├── GapCard.jsx              # Expandable card for single gap (severity, description)
│   │   │   └── CorrectiveActionList.jsx # Recommendation list under a gap card
│   │   │
│   │   └── history/
│   │       └── AnalysisRow.jsx          # Single row in history table
│   │
│   ├── pages/
│   │   ├── Dashboard.jsx                # Overview: stat cards + recent analyses
│   │   ├── UploadPage.jsx               # Upload + template select + analyze trigger
│   │   ├── AnalysisReport.jsx           # Full gap report with corrective actions
│   │   └── HistoryPage.jsx              # Paginated analysis history table
│   │
│   ├── services/
│   │   └── api.js                       # Axios instance + all API call functions
│   │                                    #   - uploadDocument(file)
│   │                                    #   - triggerAnalysis(documentId, templateId)
│   │                                    #   - getAnalysis(analysisId)
│   │                                    #   - getAnalyses(params)
│   │                                    #   - getTemplates()
│   │                                    #   - getDocuments(params)
│   │                                    #   - deleteDocument(documentId)
│   │
│   ├── hooks/
│   │   ├── useDocuments.js              # Custom hook: fetch + manage document state
│   │   ├── useAnalyses.js               # Custom hook: fetch + manage analysis state
│   │   └── useTemplates.js              # Custom hook: fetch + manage template state
│   │
│   └── utils/
│       ├── constants.js                 # API_BASE_URL, severity colors, file type config
│       └── formatters.js               # Date/time formatting, file size formatting
│
├── package.json                         # npm dependencies and scripts
├── vite.config.js                       # Vite configuration (proxy to backend)
└── .gitignore
```

### 7.3 Root Project Structure

```
pharmalens/
├── pharmalens-backend/                  # Python FastAPI backend (see 7.1)
├── pharmalens-frontend/                 # React Vite frontend (see 7.2)
├── docker-compose.yml                   # Local dev: backend + frontend
├── README.md                            # Project overview + setup instructions
└── .gitignore                           # Root-level ignores
```

---

## 8. API Architecture

### 8.1 Base URL

| Environment | Backend URL | Frontend URL |
|-------------|------------|--------------|
| **Local Dev** | `http://localhost:8000` | `http://localhost:5173` |
| **Production** | `https://pharmalens-api.onrender.com` | `https://pharmalens.vercel.app` |

### 8.2 Endpoint Map

| Method | Endpoint | Description | Auth |
|--------|----------|-------------|------|
| POST | `/api/documents` | Upload PDF/DOCX document | — |
| GET | `/api/documents` | List all documents (paginated) | — |
| GET | `/api/documents/:id` | Get document details + extracted text | — |
| DELETE | `/api/documents/:id` | Delete document + cascade | — |
| POST | `/api/templates` | Create compliance template with sections | — |
| GET | `/api/templates` | List all templates | — |
| GET | `/api/templates/:id` | Get template with sections | — |
| PUT | `/api/templates/:id` | Update template | — |
| DELETE | `/api/templates/:id` | Delete template | — |
| POST | `/api/analyses` | Trigger compliance analysis | — |
| GET | `/api/analyses` | List analyses (filter by document_id, status) | — |
| GET | `/api/analyses/:id` | Get full analysis report | — |

### 8.3 Response Format

All API responses follow a consistent JSON structure:

```json
// Success (single resource)
{ "id": "uuid", "field": "value", ... }

// Success (collection)
[ { "id": "uuid", ... }, ... ]

// Error
{ "detail": "Human-readable error message" }
```

### 8.4 Template Contract Compatibility

The current database and ORM contract remains canonical: templates use `governing_body` and `version`, while sections use `section_code`, `title`, `requirement_text`, and `mandatory`. The REST API accepts legacy PRD payload names (`framework`, `section_name`, section-level `description`, and `is_mandatory`) and translates them at the Pydantic boundary. Responses expose read-only aliases for those legacy names. No PostgreSQL/Supabase columns are renamed, and no migration is required for this compatibility layer.

---

## 9. Environment Variables

### Backend `.env`

```env
# Supabase Docker/CLI configuration
SUPABASE_DB_URL=postgresql+asyncpg://postgres:postgres@127.0.0.1:54322/postgres
SUPABASE_URL=http://127.0.0.1:54321
SUPABASE_PUBLISHABLE_KEY=your-local-publishable-key

# Supabase Storage
STORAGE_BUCKET=pharmalens-docs

# LLM Configuration (at least one required)
GOOGLE_API_KEY=your-google-api-key
OPENAI_API_KEY=your-openai-api-key
LLM_PROVIDER=google           # "google" or "openai"

# Server Configuration
HOST=0.0.0.0
PORT=8000
CORS_ORIGINS=http://localhost:5173,https://pharmalens.vercel.app

# Logging
LOG_LEVEL=INFO
```

### Frontend `.env`

```env
VITE_API_BASE_URL=http://localhost:8000
```

---

## 10. Deployment Architecture

```
┌──────────────────────────────────────────────────────────────┐
│                       PRODUCTION                              │
│                                                              │
│  ┌─────────────────┐     ┌──────────────────────────────┐   │
│  │   Vercel         │     │         Render                │   │
│  │                  │     │                              │   │
│  │  React SPA       │────►│  Docker Container            │   │
│  │  (Static Build)  │REST │  FastAPI + Uvicorn           │   │
│  │                  │     │                              │   │
│  └─────────────────┘     └──────────────┬───────────────┘   │
│                                          │                    │
│                              ┌───────────▼──────────────┐    │
│                              │  Supabase Docker Stack   │    │
│                              │                          │    │
│                              │  PostgreSQL + Storage    │    │
│                              │                          │    │
│                              └──────────────────────────┘    │
│                                                              │
│  ┌──────────────────────────────────────────────────────┐    │
│  │              External APIs                            │    │
│  │  Google Gemini API / OpenAI API                      │    │
│  └──────────────────────────────────────────────────────┘    │
│                                                              │
└──────────────────────────────────────────────────────────────┘
```

---

## 11. Local Development Setup

### Prerequisites

- Python 3.11+
- Node.js 18+
- Docker Desktop and the Supabase CLI
- A Google Gemini API key or OpenAI API key

### Backend Setup

```bash
cd pharmalens-backend
python -m venv venv
source venv/bin/activate       # Windows: venv\Scripts\activate
pip install -r requirements.txt
Update pharmalens-backend/.env # Configure local Supabase Docker values
alembic upgrade head           # Run database migrations
uvicorn main:app --reload --port 8000
```

### Frontend Setup

```bash
cd pharmalens-frontend
npm install
Update pharmalens-frontend/.env # Set VITE_API_BASE_URL
npm run dev                    # Starts on http://localhost:5173
```

---
