# Product Requirements Document — PharmaLens Backend

## 1. Basic Information

| Field | Details |
|-------|---------|
| **Feature Name** | PharmaLens — AI-Powered Regulatory Compliance Copilot (Backend) |
| **Owner** | Bhuvan Nagesh |
| **Developers** | Bhuvan N |
| **Contributors** | — |
| **Created Date** | 28-09-2026 |
| **Last Updated** | 28-09-2026 |
| **Status** | Planning |
| **Priority** | High |
| **Related Issue / Task** | PHARMALENS-BACKEND-001 |

---

## 2. Problem Statement / Feature Explanation

### Problem

Life-sciences and pharmaceutical companies operate under strict regulatory frameworks (FDA 21 CFR Part 211, ICH Q10, EU GMP Annex 15). Their quality teams routinely author and review critical documents — Standard Operating Procedures (SOPs), Batch Manufacturing Records (BMRs), deviation reports, and validation protocols.

Today, compliance review is **entirely manual**: a quality analyst reads each document, mentally maps its sections against regulatory requirements, identifies what's missing or non-compliant, and writes corrective action memos. This process is:

1. **Slow** — a single SOP compliance review can take hours
2. **Inconsistent** — different analysts may flag different gaps on the same document
3. **Unscalable** — as the number of documents grows, human reviewers become bottlenecks

**Why are we building this?**
- To demonstrate that AI (specifically multi-agent LangGraph pipelines) can be embedded directly into pharmaceutical quality workflows — not as a standalone chatbot, but as an integral product feature
- To build a portfolio-ready, full-stack SaaS application that mirrors the exact problem domain of AIVOA.AI's Quality Management System
- To gain hands-on experience with Python, FastAPI, LangGraph, Generative AI, and PostgreSQL in a real product context

### Feature Explanation

PharmaLens is a **full-stack AI-powered regulatory compliance copilot**. The backend is responsible for:

1. **Document Ingestion** — Accepting PDF/DOCX uploads via REST API, extracting text content, and storing raw + processed data in PostgreSQL
2. **Multi-Agent Compliance Pipeline** — A LangGraph stateful graph with 4 specialized AI agents that process each uploaded document through a structured analysis workflow
3. **Regulatory Template Management** — CRUD APIs for managing compliance templates (e.g., "FDA SOP Template" with required sections)
4. **Report Generation & Storage** — Persisting compliance gap reports, corrective action recommendations, and full audit trails
5. **Analysis History** — Exposing all past analyses per user/document for dashboard retrieval

### Document Parser Provider Strategy

The ingestion endpoint keeps the native PyPDF2/pdfplumber and python-docx extractors as the
deployment-safe default. An optional Dolphin-v2 provider can improve extraction from scanned,
photographed, layout-heavy, and table-heavy PDFs by performing page layout analysis followed by
element-level transcription. It is selected through environment configuration and is never
required for the backend to start:

| Setting | Behavior |
|---|---|
| `DOCUMENT_PARSER_PROVIDER=native` | Always use the lightweight native extractors (default). |
| `DOCUMENT_PARSER_PROVIDER=auto` | Use native PDF text first; use Dolphin only when the result is empty or very short. |
| `DOCUMENT_PARSER_PROVIDER=dolphin` | Try Dolphin for PDFs, then fall back to native extraction if the optional runtime is unavailable or fails. |

Dolphin-v2 is a local optional runtime because its model weights and vision dependencies are too
large to make a free, CPU-only deployment prerequisite. `DOCX` uploads continue to use
python-docx. The original file remains in Supabase Storage, while the selected parser output is
stored in the existing `documents.extracted_text` column; no database migration is required.

```
                    ┌──────────────────────────┐
                    │      FastAPI Server       │
                    │                          │
  Upload PDF/DOCX ──► POST /api/documents      │
                    │   ↓ Text Extraction       │
                    │   ↓ Store in PostgreSQL   │
                    │                          │
  Trigger Analysis ─► POST /api/analyses       │
                    │   ↓ LangGraph Pipeline    │
                    │   ┌──────────────────┐   │
                    │   │ Agent 1: Parser   │   │
                    │   │      ↓            │   │
                    │   │ Agent 2: Mapper   │   │
                    │   │      ↓            │   │
                    │   │ Agent 3: Analyzer │   │
                    │   │      ↓            │   │
                    │   │ Agent 4: Advisor  │   │
                    │   └──────────────────┘   │
                    │   ↓ Store Report          │
                    │                          │
  Get Report ───────► GET /api/analyses/:id    │
  Get History ──────► GET /api/analyses        │
  Manage Templates ─► /api/templates (CRUD)    │
                    └──────────────────────────┘
                              │
                    ┌─────────▼─────────┐
                    │    PostgreSQL      │
                    │  documents         │
                    │  analyses          │
                    │  compliance_templates │
                    │  analysis_gaps     │
                    │  corrective_actions│
                    │  audit_logs        │
                    └───────────────────┘
```

### Self-Hosted Supabase Docker Strategy

PharmaLens uses the self-hosted Supabase Docker stack as its single database and file-storage platform. The stack provides PostgreSQL, Storage, API, and Studio using persistent Docker volumes. The same stack runs locally and on a Docker-capable deployment host, avoiding Supabase Cloud free-tier quotas and preserving deployment parity.

The backend uses only `SUPABASE_DB_URL`, `SUPABASE_URL`, `SUPABASE_PUBLISHABLE_KEY`, and `STORAGE_BUCKET`. There is no standalone PostgreSQL mode, no dual-write behavior, and no storage fallback to the application filesystem.

---

## 3. Objective

### Goals

- **Goal 1:** Build a production-grade FastAPI backend with RESTful API design patterns (routers, dependency injection, Pydantic schemas, async endpoints)
- **Goal 2:** Implement a LangGraph multi-agent pipeline with 4 specialized agents, each with distinct system prompts and responsibilities
- **Goal 3:** Integrate document text extraction for PDF and DOCX file formats
- **Goal 4:** Design a normalized PostgreSQL schema for documents, analyses, templates, gaps, corrective actions, and audit logs
- **Goal 5:** Expose clean, documented REST APIs for the React frontend to consume
- **Goal 6:** Persist all AI agent outputs and user actions in an audit trail for compliance traceability

### Success Metrics

- All API endpoints return correct HTTP status codes and JSON payloads
- LangGraph pipeline processes a document through all 4 agents and produces a structured gap report
- Document text extraction works for PDF and DOCX formats
- Analysis history is retrievable per document with full audit trail
- API response times are reasonable for the expected document sizes

---

## 4. User Flow

```
Frontend sends POST /api/documents (multipart/form-data with file)
  ↓
Backend extracts text from PDF/DOCX (PyPDF2 / python-docx)
  ↓
Stores raw file metadata + extracted text in `documents` table
  ↓
Returns document_id to frontend
  ↓
Frontend sends POST /api/analyses { document_id, template_id }
  ↓
Backend loads document text + compliance template from DB
  ↓
Invokes LangGraph pipeline:
  ↓
  Agent 1 (Document Parser): Extracts and labels document sections
  ↓
  Agent 2 (Regulatory Mapper): Maps extracted sections against template required sections
  ↓
  Agent 3 (Gap Analyzer): Identifies missing/incomplete sections, classifies severity (Critical/Major/Minor)
  ↓
  Agent 4 (Corrective Action Recommender): Generates plain-English recommendations for each gap
  ↓
Pipeline output stored in `analyses`, `analysis_gaps`, `corrective_actions` tables
  ↓
Audit log entry created with timestamps
  ↓
Returns analysis_id to frontend
  ↓
Frontend fetches GET /api/analyses/:analysis_id
  ↓
Backend returns full analysis report (gaps, severities, recommendations, metadata)
  ↓
Frontend fetches GET /api/analyses?document_id=xxx
  ↓
Backend returns analysis history for that document
```

---

## 5. Feature Impact

### Impacted Modules

| Module | Impact Level |
|--------|--------------|
| FastAPI application (main server) | High — core application setup, routers, middleware |
| LangGraph pipeline (`agents/compliance_pipeline.py`) | High — all 4 agents authored and orchestrated |
| Document processing (`services/document_processor.py`) | High — text extraction from PDF/DOCX |
| Database models (`models/`) | High — all tables and relationships |
| API routers (`routers/`) | High — all endpoint definitions |

### Impacted APIs

| API | Purpose |
|-----|---------|
| `POST /api/documents` | Upload and process a document (PDF/DOCX) |
| `GET /api/documents` | List all uploaded documents |
| `GET /api/documents/:id` | Get a specific document's metadata and extracted text |
| `DELETE /api/documents/:id` | Delete a document and its associated analyses |
| `POST /api/analyses` | Trigger a new compliance analysis on a document |
| `GET /api/analyses` | List all analyses (with optional `document_id` filter) |
| `GET /api/analyses/:id` | Get full analysis report (gaps, recommendations, audit trail) |
| `GET /api/templates` | List all compliance templates |
| `POST /api/templates` | Create a new compliance template |
| `GET /api/templates/:id` | Get a specific template with its required sections |
| `PUT /api/templates/:id` | Update a compliance template |
| `DELETE /api/templates/:id` | Delete a compliance template |

Analysis execution is asynchronous. `POST /api/analyses` commits the processing record and returns `202 Accepted`; the worker runs the LangGraph graph with an independent async database session. `GET /api/analyses/:id` can therefore return `processing`, `completed`, or `failed`. Completed results and failure details are persisted with bounded error text and audit events (`analysis_completed` or `analysis_failed`).

### Impacted Database

| Table | Purpose |
|-------|---------|
| `documents` | Uploaded documents — metadata, extracted text, file path |
| `compliance_templates` | Regulatory compliance templates with required sections |
| `template_sections` | Individual required sections within a template |
| `analyses` | Analysis runs — links document to template, stores status and timestamps |
| `analysis_gaps` | Individual gaps found — section name, severity, description |
| `corrective_actions` | AI-generated recommendations — linked to specific gaps |
| `audit_logs` | Timestamped log of every action (upload, analysis trigger, completion) |

---

## 6. Implementation Breakdown

### Backend — FastAPI Application Structure

```
pharmalens-backend/
├── main.py                          # FastAPI app entry point, CORS, lifespan
├── config.py                        # Environment variables, DB URL, API keys
├── requirements.txt                 # Python dependencies
│
├── app/api/
│   ├── documents.py                 # Document upload, list, get, delete
│   ├── analyses.py                  # Trigger analysis, get report, list history
│   └── templates.py                 # CRUD for compliance templates
│
├── models/
│   ├── database.py                  # SQLAlchemy engine, session, Base
│   ├── document.py                  # Document model
│   ├── template.py                  # ComplianceTemplate + TemplateSection models
│   ├── analysis.py                  # Analysis, AnalysisGap, CorrectiveAction models
│   └── audit_log.py                 # AuditLog model
│
├── schemas/
│   ├── document.py                  # Pydantic request/response schemas
│   ├── analysis.py                  # Analysis request/response schemas
│   └── template.py                  # Template request/response schemas
│
├── services/
│   ├── document_processor.py        # PDF/DOCX text extraction logic
│   ├── analysis_service.py          # Background execution and persistence
│   └── scoring.py                   # Deterministic compliance scoring
│
├── agents/
│   ├── compliance_pipeline.py       # LangGraph StateGraph definition
│   ├── document_parser_agent.py     # Agent 1: Extract + label sections
│   ├── regulatory_mapper_agent.py   # Agent 2: Map sections to template
│   ├── gap_analyzer_agent.py        # Agent 3: Identify gaps + classify severity
│   └── corrective_action_agent.py   # Agent 4: Generate recommendations
│
└── utils/
    └── logger.py                    # Structured logging
```

### Backend — LangGraph Multi-Agent Pipeline

The pipeline is implemented as a **LangGraph StateGraph** with a shared state object passed through 4 sequential nodes:

**State Schema:**
```python
class ComplianceState(TypedDict):
    document_text: str
    document_sections: list[dict]        # Output of Agent 1
    template_sections: list[dict]        # Loaded from DB
    section_mapping: list[dict]          # Output of Agent 2
    gaps: list[dict]                     # Output of Agent 3
    corrective_actions: list[dict]       # Output of Agent 4
    metadata: dict                       # document_id, template_id, timestamps
```

**Pipeline Graph:**
```
START → document_parser → regulatory_mapper → gap_analyzer → corrective_action_recommender → END
```

Each agent node:
1. Receives the full `ComplianceState`
2. Makes an LLM call (OpenAI GPT / Google Gemini) with a specialized system prompt
3. Parses the structured JSON response
4. Updates its designated state fields
5. Returns the updated state for the next node

### Backend — Database Schema (PostgreSQL)

**documents:**
| Column | Type | Description |
|--------|------|-------------|
| id | UUID (PK) | Primary key |
| filename | VARCHAR(255) | Original uploaded filename |
| file_type | VARCHAR(10) | "pdf" or "docx" |
| file_size_bytes | INTEGER | File size |
| extracted_text | TEXT | Full extracted text content |
| uploaded_at | TIMESTAMP | Upload timestamp |

**compliance_templates:**
| Column | Type | Description |
|--------|------|-------------|
| id | UUID (PK) | Primary key |
| name | VARCHAR(255) | Template name (e.g., "FDA SOP Template") |
| description | TEXT | Description of the regulatory framework |
| framework | VARCHAR(100) | "FDA 21 CFR Part 211", "ICH Q10", etc. |
| created_at | TIMESTAMP | Creation timestamp |

**template_sections:**
| Column | Type | Description |
|--------|------|-------------|
| id | UUID (PK) | Primary key |
| template_id | UUID (FK → compliance_templates) | Parent template |
| section_name | VARCHAR(255) | Required section name |
| description | TEXT | What this section should contain |
| is_mandatory | BOOLEAN | Whether this section is mandatory |
| order_index | INTEGER | Display order |

**analyses:**
| Column | Type | Description |
|--------|------|-------------|
| id | UUID (PK) | Primary key |
| document_id | UUID (FK → documents) | Analyzed document |
| template_id | UUID (FK → compliance_templates) | Template used for analysis |
| status | VARCHAR(20) | "pending", "processing", "completed", "failed" |
| total_gaps | INTEGER | Total gaps found |
| critical_gaps | INTEGER | Critical severity gaps |
| major_gaps | INTEGER | Major severity gaps |
| minor_gaps | INTEGER | Minor severity gaps |
| started_at | TIMESTAMP | When analysis began |
| completed_at | TIMESTAMP | When analysis finished |
| created_at | TIMESTAMP | Record creation |

**analysis_gaps:**
| Column | Type | Description |
|--------|------|-------------|
| id | UUID (PK) | Primary key |
| analysis_id | UUID (FK → analyses) | Parent analysis |
| section_name | VARCHAR(255) | Which required section has the gap |
| severity | VARCHAR(20) | "critical", "major", "minor" |
| gap_type | VARCHAR(50) | "missing", "incomplete", "non_compliant" |
| description | TEXT | AI-generated explanation of the gap |
| document_excerpt | TEXT | Relevant excerpt from the document (if any) |

**corrective_actions:**
| Column | Type | Description |
|--------|------|-------------|
| id | UUID (PK) | Primary key |
| gap_id | UUID (FK → analysis_gaps) | Which gap this addresses |
| recommendation | TEXT | AI-generated corrective action text |
| priority | VARCHAR(20) | "high", "medium", "low" |

**audit_logs:**
| Column | Type | Description |
|--------|------|-------------|
| id | UUID (PK) | Primary key |
| entity_type | VARCHAR(50) | "document", "analysis", "template" |
| entity_id | UUID | ID of the affected entity |
| action | VARCHAR(50) | "uploaded", "analysis_triggered", "analysis_completed", etc. |
| details | JSONB | Additional context |
| performed_at | TIMESTAMP | When the action occurred |

### Gen AI

- **LLM Provider:** OpenAI GPT-4o-mini or Google Gemini 1.5 Flash (configurable via environment variable)
- **Agent 1 System Prompt:** "You are a pharmaceutical document parser. Given the full text of a quality document, extract and label all distinct sections. Return a JSON array of sections with `section_title` and `section_content` fields."
- **Agent 2 System Prompt:** "You are a regulatory compliance mapper. Given a list of document sections and a list of required template sections, map each template section to the best-matching document section. Return a JSON array with `template_section`, `matched_document_section` (or null if no match), and `match_confidence` (high/medium/low/none)."
- **Agent 3 System Prompt:** "You are a pharmaceutical compliance gap analyzer. Given the section mapping, identify all gaps (missing, incomplete, or non-compliant sections). Classify each gap as critical, major, or minor. Return a JSON array with `section_name`, `severity`, `gap_type`, and `description`."
- **Agent 4 System Prompt:** "You are a corrective action advisor for pharmaceutical quality management. Given a list of compliance gaps, generate specific, actionable corrective action recommendations for each gap. Return a JSON array with `gap_section`, `recommendation`, and `priority`."

### Dependencies (requirements.txt)

```
fastapi==0.115.*
uvicorn[standard]==0.30.*
sqlalchemy==2.0.*
asyncpg==0.30.*
alembic==1.14.*
python-multipart==0.0.*
pydantic==2.10.*
PyPDF2==3.0.*
python-docx==1.1.*
langgraph==0.4.*
langchain-core==0.3.*
langchain-openai==0.3.*
langchain-google-genai==2.1.*
python-dotenv==1.1.*
```

---

## 7. Functional Requirements

| ID | Requirement | Acceptance Criteria |
|----|-------------|---------------------|
| FR-1 | Document upload accepts PDF and DOCX files | `POST /api/documents` returns 201 with `document_id`; extracted text is non-empty |
| FR-2 | Document text extraction works for PDF files | PyPDF2 extracts text from all pages; stored in `extracted_text` column |
| FR-3 | Document text extraction works for DOCX files | python-docx extracts text from all paragraphs; stored in `extracted_text` column |
| FR-4 | Unsupported file types are rejected | `POST /api/documents` returns 400 with `Unsupported file type. Only PDF and DOCX files are accepted` |
| FR-5 | Compliance templates can be created with required sections | `POST /api/templates` returns 201 with template and its sections |
| FR-6 | Analysis can be triggered on a document with a template | `POST /api/analyses` returns 202 with `analysis_id` and status "processing" |
| FR-7 | LangGraph pipeline executes all 4 agents in sequence | Analysis status transitions: pending → processing → completed |
| FR-8 | Agent 1 extracts document sections | `document_sections` field in state is populated with section titles and content |
| FR-9 | Agent 2 maps document sections to template sections | `section_mapping` field shows each template section with its match (or null) |
| FR-10 | Agent 3 identifies compliance gaps with severity | `gaps` field contains gaps classified as critical, major, or minor |
| FR-11 | Agent 4 generates corrective action recommendations | `corrective_actions` field contains actionable recommendations per gap |
| FR-12 | Analysis results are persisted in PostgreSQL | `analyses`, `analysis_gaps`, and `corrective_actions` tables populated |
| FR-13 | Analysis report is retrievable via API | `GET /api/analyses/:id` returns full report with gaps and recommendations |
| FR-14 | Analysis history is retrievable per document | `GET /api/analyses?document_id=xxx` returns all analyses for that document |
| FR-15 | Audit log captures all actions with timestamps | `audit_logs` table has entries for uploads, analysis triggers, and completions |
| FR-16 | Invalid document_id or template_id returns 404 | `POST /api/analyses` with non-existent IDs returns 404 |
| FR-17 | Duplicate analysis on same document+template is allowed | Each analysis creates a new record (version comparison possible) |
| FR-18 | Failed LLM calls are handled gracefully | Analysis status set to "failed" with error details; 500 not propagated to client |

---

## 8. API Changes

### All Endpoints

| Endpoint | Method | Purpose | Request Body / Params |
|----------|--------|---------|----------------------|
| `/api/documents` | POST | Upload a document | multipart/form-data: `file` (PDF/DOCX) |
| `/api/documents` | GET | List all documents | Query: `?page=1&limit=10` |
| `/api/documents/:id` | GET | Get document details + extracted text | Path: `id` (UUID) |
| `/api/documents/:id` | DELETE | Delete document + associated analyses | Path: `id` (UUID) |
| `/api/analyses` | POST | Trigger compliance analysis | JSON: `{ "document_id": "uuid", "template_id": "uuid" }` |
| `/api/analyses` | GET | List all analyses | Query: `?document_id=uuid&status=completed&page=1&limit=10` |
| `/api/analyses/:id` | GET | Get full analysis report | Path: `id` (UUID) |
| `/api/templates` | POST | Create compliance template | JSON: `{ "name": "...", "framework": "...", "description": "...", "sections": [...] }` |
| `/api/templates` | GET | List all templates | — |
| `/api/templates/:id` | GET | Get template with sections | Path: `id` (UUID) |
| `/api/templates/:id` | PUT | Update template | JSON: same as POST |
| `/api/templates/:id` | DELETE | Delete template | Path: `id` (UUID) |

### Canonical Schema and Legacy API Compatibility

The live SQLAlchemy/Supabase schema is canonical and is not renamed for compatibility. Template records use `governing_body`, `version`, `section_code`, `title`, `requirement_text`, and `mandatory`.

For clients built from earlier PRD examples, the API also accepts these request aliases:

| Legacy request field | Canonical field | Translation |
|----------------------|-----------------|-------------|
| `framework` | `governing_body` | `FDA`, `EMA`, `EU GMP`, `WHO`, and `ICH` prefixes are mapped to the supported governing body |
| `section_name` | `title` | Section display name |
| Section-level `description` | `requirement_text` | Normative requirement text |
| `is_mandatory` | `mandatory` | Boolean mandatory flag |

When a legacy template omits `version`, the API stores `unspecified`. When a legacy section omits `section_code`, the API derives a bounded `custom-*` code from its section name. Responses include both canonical fields and read-only aliases (`framework`, `section_name`, `description`, and `is_mandatory`) so existing clients can migrate without a database or Supabase migration.

### Request Payload — Create Template

```json
{
  "name": "FDA SOP Compliance Template",
  "framework": "FDA 21 CFR Part 211",
  "description": "Standard Operating Procedure template based on FDA manufacturing regulations",
  "sections": [
    {
      "section_name": "Purpose and Scope",
      "description": "Clear statement of the SOP's purpose, scope, and applicability",
      "is_mandatory": true,
      "order_index": 1
    },
    {
      "section_name": "Responsibilities",
      "description": "Roles and responsibilities of personnel involved",
      "is_mandatory": true,
      "order_index": 2
    },
    {
      "section_name": "Procedure Steps",
      "description": "Detailed step-by-step procedure instructions",
      "is_mandatory": true,
      "order_index": 3
    },
    {
      "section_name": "Safety Precautions",
      "description": "Safety measures and PPE requirements",
      "is_mandatory": true,
      "order_index": 4
    },
    {
      "section_name": "References",
      "description": "Referenced regulatory documents, standards, and guidelines",
      "is_mandatory": false,
      "order_index": 5
    },
    {
      "section_name": "Revision History",
      "description": "Document version history with dates and change summaries",
      "is_mandatory": true,
      "order_index": 6
    }
  ]
}
```

### Response — Analysis Report (GET /api/analyses/:id)

```json
{
  "id": "analysis-uuid",
  "document": {
    "id": "doc-uuid",
    "filename": "SOP-Manufacturing-v3.pdf",
    "file_type": "pdf",
    "uploaded_at": "2026-09-28T14:00:00Z"
  },
  "template": {
    "id": "template-uuid",
    "name": "FDA SOP Compliance Template",
    "framework": "FDA 21 CFR Part 211"
  },
  "status": "completed",
  "summary": {
    "total_gaps": 3,
    "critical_gaps": 1,
    "major_gaps": 1,
    "minor_gaps": 1
  },
  "gaps": [
    {
      "id": "gap-uuid-1",
      "section_name": "Safety Precautions",
      "severity": "critical",
      "gap_type": "missing",
      "description": "The document does not contain a dedicated Safety Precautions section. FDA 21 CFR Part 211 requires documented safety procedures for manufacturing operations.",
      "corrective_actions": [
        {
          "recommendation": "Add a Safety Precautions section covering: required PPE, chemical handling procedures, emergency response protocols, and equipment safety checks per FDA guidelines.",
          "priority": "high"
        }
      ]
    },
    {
      "id": "gap-uuid-2",
      "section_name": "Revision History",
      "severity": "major",
      "gap_type": "incomplete",
      "description": "A revision history is present but lacks change summaries. Each revision entry should include the date, author, version number, and a description of changes made.",
      "corrective_actions": [
        {
          "recommendation": "Update the revision history table to include a 'Change Description' column documenting what was modified in each version.",
          "priority": "medium"
        }
      ]
    },
    {
      "id": "gap-uuid-3",
      "section_name": "References",
      "severity": "minor",
      "gap_type": "incomplete",
      "description": "The references section lists internal documents but does not cite the applicable FDA regulatory codes.",
      "corrective_actions": [
        {
          "recommendation": "Add explicit references to FDA 21 CFR Part 211, Subparts relevant to this SOP's scope.",
          "priority": "low"
        }
      ]
    }
  ],
  "started_at": "2026-09-28T14:01:00Z",
  "completed_at": "2026-09-28T14:01:18Z",
  "created_at": "2026-09-28T14:01:00Z"
}
```

---

## 9. Database Changes

### Tables

| Table | Purpose |
|-------|---------|
| `documents` | Stores uploaded document metadata and extracted text |
| `compliance_templates` | Regulatory compliance template definitions |
| `template_sections` | Required sections within each template |
| `analyses` | Analysis run records with status and summary counts |
| `analysis_gaps` | Individual gaps found during analysis |
| `corrective_actions` | AI-generated corrective action recommendations |
| `audit_logs` | Timestamped action log for compliance traceability |

### Index Requirements

| Table | Index | Type |
|-------|-------|------|
| `analyses` | `(document_id)` | B-tree |
| `analyses` | `(template_id)` | B-tree |
| `analyses` | `(status)` | B-tree |
| `analysis_gaps` | `(analysis_id)` | B-tree |
| `analysis_gaps` | `(severity)` | B-tree |
| `corrective_actions` | `(gap_id)` | B-tree |
| `audit_logs` | `(entity_type, entity_id)` | Composite B-tree |
| `audit_logs` | `(performed_at)` | B-tree |

### Public Database Security

Migration `002_enable_public_rls` enables row-level security on every application table and on `alembic_version`. Because v1 has no end-user authentication, no `anon` or `authenticated` table policies are granted. Direct Supabase Data API access is therefore denied by default; the FastAPI server uses the configured trusted PostgreSQL connection for all application operations. Storage authorization remains bucket-scoped through the separate Storage policies.

---

## 10. Validation Rules

| Field | Validation | Error Message |
|-------|------------|---------------|
| `file` (upload) | Must be present; extension must be `.pdf` or `.docx` | `No file uploaded` / `Unsupported file type. Only PDF and DOCX files are accepted` |
| `file` (upload) | Max size 300MB | `File size exceeds 300MB limit` |
| `document_id` (analysis) | Must exist in `documents` table | `Document not found` |
| `template_id` (analysis) | Must exist in `compliance_templates` table | `Compliance template not found` |
| `template.name` | Non-empty string, max 255 chars | `Template name is required` |
| `template.framework` | Non-empty string, max 100 chars | `Regulatory framework is required` |
| `template.sections` | At least 1 section | `Template must have at least one required section` |
| `section.section_name` | Non-empty string, max 255 chars | `Section name is required` |
| `id` (path params) | Valid UUID format | `Invalid ID format` |
| `page` (query) | Positive integer, default 1 | `Page must be a positive integer` |
| `limit` (query) | Integer 1–100, default 10 | `Limit must be between 1 and 100` |

---

## 11. Edge Cases

### Document Processing Edge Cases

- PDF with scanned images (no extractable text) → extracted text is empty → analysis runs but Agent 1 returns "No text content found" → gap report shows all sections as "missing"
- Corrupted PDF that PyPDF2 cannot read → catch exception → return 400 `Unable to process this file. The document may be corrupted`
- Empty DOCX (no paragraphs or tables) → extracted text is empty → same behavior as scanned PDF
- DOCX tables → table rows are extracted in document order with cell values preserved as pipe-separated text
- Upload content does not match its declared PDF/DOCX type → reject with 400 before extraction or Storage upload
- Very large document (100+ pages) → text extraction succeeds; LLM processes truncated context if token limit exceeded → Agent system prompts handle gracefully
- Backend restart during analysis → startup recovery marks stale `processing` rows as `failed` with an audit event
- Malformed structured agent output → background persistence rejects it atomically and records a safe `failed` status

### LangGraph Pipeline Edge Cases

- LLM API timeout → catch exception → set analysis status to "failed" → log error in audit trail
- LLM returns malformed JSON → catch parsing exception → retry once with clarification prompt → if still fails, set status to "failed"
- LLM rate limit hit → exponential backoff with 3 retries → if exhausted, set status to "failed"
- Template with 0 matching sections in document → all gaps classified as "critical" → valid analysis result

### API Edge Cases

- Delete a document that has associated analyses → cascade delete analyses, gaps, corrective_actions, audit_logs
- Trigger analysis while another is still "processing" for same document → allowed (creates new analysis record)
- GET analysis that is still "processing" → return current status with empty gaps/actions
- Concurrent POST /api/analyses with same document_id + template_id → both succeed (separate analysis records)

### Database Edge Cases

- UUID collision → statistically negligible; handled by PK constraint
- Long extracted text (> 1MB) → TEXT column has no limit in PostgreSQL; works fine
- Null extracted_text after upload → set to empty string, not NULL

---

## 12. Error Handling

| Scenario | Expected Behaviour |
|----------|-------------------|
| No file in upload request | 400 JSON `{ "detail": "No file uploaded" }` |
| Unsupported file type | 400 JSON `{ "detail": "Unsupported file type. Only PDF and DOCX files are accepted" }` |
| File too large (> 300MB) | 413 JSON `{ "detail": "File size exceeds 300MB limit" }` |
| Corrupted file | 400 JSON `{ "detail": "Unable to process this file. The document may be corrupted" }` |
| Document not found | 404 JSON `{ "detail": "Document not found" }` |
| Template not found | 404 JSON `{ "detail": "Compliance template not found" }` |
| Analysis not found | 404 JSON `{ "detail": "Analysis not found" }` |
| Invalid UUID format | 422 JSON `{ "detail": "Invalid ID format" }` |
| Missing required field | 422 JSON (Pydantic validation error with field details) |
| LLM API failure | Analysis status set to "failed"; audit log entry; API returns analysis with `status: "failed"` |
| Internal server error | 500 JSON `{ "detail": "Internal server error" }` (logged to console) |

---

## 13. Test Cases

| Test ID | Scenario | Steps | Expected Result |
|---------|----------|-------|-----------------|
| TC-001 | Upload PDF document | POST /api/documents with a valid PDF | 201, document_id returned, extracted_text non-empty |
| TC-002 | Upload DOCX document | POST /api/documents with a valid DOCX | 201, document_id returned, extracted_text non-empty |
| TC-003 | Upload unsupported file | POST /api/documents with a .txt file | 400, error message about unsupported type |
| TC-004 | Upload no file | POST /api/documents with empty body | 400, "No file uploaded" |
| TC-005 | Create compliance template | POST /api/templates with valid body | 201, template with sections returned |
| TC-006 | Create template without sections | POST /api/templates with empty sections array | 422, validation error |
| TC-007 | Trigger analysis | POST /api/analyses with valid document_id and template_id | 202, analysis_id returned with status "processing" |
| TC-008 | Analysis with invalid document_id | POST /api/analyses with non-existent UUID | 404, "Document not found" |
| TC-009 | Analysis with invalid template_id | POST /api/analyses with non-existent UUID | 404, "Compliance template not found" |
| TC-010 | Get completed analysis report | GET /api/analyses/:id after pipeline completes | 200, full report with gaps and corrective actions |
| TC-011 | Get analysis history for document | GET /api/analyses?document_id=xxx | 200, list of all analyses for that document |
| TC-012 | Pipeline Agent 1 output | Check analysis state after pipeline | document_sections array is populated |
| TC-013 | Pipeline Agent 3 severity classification | Check gaps in analysis report | Each gap has severity: critical, major, or minor |
| TC-014 | Pipeline Agent 4 recommendations | Check corrective_actions in report | Each gap has at least one recommendation |
| TC-015 | Delete document cascades | DELETE /api/documents/:id with analyses | Document, analyses, gaps, actions all deleted |
| TC-016 | Audit log entries created | Check audit_logs table after operations | Entries for upload, analysis trigger, completion |
| TC-017 | LLM failure handling | Simulate LLM timeout | Analysis status "failed", audit log entry |
| TC-018 | List documents with pagination | GET /api/documents?page=1&limit=5 | Max 5 results returned |

---

## 14. Development & Testing Checklist

### Development

- [ ] FastAPI application structure created (main.py, routers, models, schemas, services, agents)
- [ ] PostgreSQL database schema designed and migration scripts written (Alembic)
- [ ] Document upload endpoint with PDF/DOCX text extraction implemented
- [ ] Compliance template CRUD endpoints implemented
- [ ] LangGraph StateGraph with 4 agent nodes implemented
- [ ] Agent system prompts authored and tested with sample documents
- [x] Analysis trigger endpoint with pipeline invocation implemented
- [x] Analysis report retrieval endpoint implemented
- [x] Audit logging integrated across analysis trigger, completion, and failure transitions
- [x] Error handling and validation rules implemented
- [ ] CORS middleware configured for frontend access
- [ ] Environment variable configuration (.env) set up

### Testing

- [ ] All API endpoints tested with valid and invalid inputs
- [ ] LangGraph pipeline tested end-to-end with a sample SOP document
- [ ] Edge cases tested (corrupted files, empty documents, LLM failures)
- [ ] Database cascade deletes verified

### Final Verification

- [ ] All endpoints return correct HTTP status codes
- [ ] Pydantic schemas enforce validation rules
- [ ] LangGraph pipeline produces structured, parseable output
- [ ] Audit trail captures all user actions

---

## 15. Acceptance Criteria

- [ ] `POST /api/documents` accepts PDF and DOCX, extracts text, returns document_id
- [ ] `POST /api/templates` creates a compliance template with required sections
- [ ] `POST /api/analyses` triggers LangGraph pipeline and returns analysis_id
- [ ] LangGraph pipeline processes document through all 4 agents sequentially
- [ ] `GET /api/analyses/:id` returns full compliance gap report with severity and recommendations
- [ ] All gaps are classified as critical, major, or minor
- [ ] Every gap has at least one corrective action recommendation
- [ ] Audit log has entries for all operations
- [ ] Invalid inputs return appropriate 4xx error responses
- [ ] LLM failures are handled gracefully (status = "failed")

---

## 16. Risks & Dependencies

### Risks

| Risk | Mitigation |
|------|-----------|
| LLM API costs during development/testing | Use GPT-4o-mini or Gemini Flash (cheapest models); mock LLM responses for unit tests |
| LLM output format inconsistency | Use structured output (JSON mode) with explicit schema in system prompts; add retry with clarification |
| Large documents exceeding LLM context window | Implement chunking strategy in Agent 1; process sections independently |
| PyPDF2 fails on certain PDF formats | Add fallback to pdfplumber library |

### Technical Dependencies

- OpenAI API key or Google Gemini API key (at least one required)
- Docker Desktop plus the Supabase CLI for local development and deployment
- Python 3.11+

### External Dependencies

- LangGraph library (v0.4+)
- LangChain Core (v0.3+)
- FastAPI (v0.115+)

---

## 17. Estimated Timeline

| Task | Estimate |
|------|----------|
| Project setup (FastAPI, PostgreSQL, Alembic migrations) | 1 day |
| Document upload + text extraction service | 1 day |
| Compliance template CRUD endpoints | 0.5 days |
| LangGraph pipeline (4 agents) + agent prompts | 2 days |
| Analysis trigger + report retrieval endpoints | 1 day |
| Audit logging + error handling | 0.5 days |
| Testing + edge cases + debugging | 1 day |
| **Total** | **7 days** |

---
