# PharmaLens — Phase-by-Phase Implementation Plan

> **Project:** PharmaLens — AI-Powered Regulatory Compliance Copilot  
> **Author:** Bhuvan Nagesh  
> **Created:** 29-09-2026  
> **Status:** Implementation Master Blueprint  
> **Reference Documents:**  
> - Architecture: [PharmaLens_Architecture.md](file:///d:/Resume/PharmaLens_Architecture.md)  
> - Rules & Standards: [PharmaLens_Rules.md](file:///d:/Resume/PharmaLens_Rules.md)  
> - Backend PRD: [PRD_PharmaLens_Backend.md](file:///d:/Resume/PRD_PharmaLens_Backend.md)  
> - Frontend PRD: [PRD_PharmaLens_Frontend.md](file:///d:/Resume/PRD_PharmaLens_Frontend.md)  
> - Design System: [PharmaLens_Design.md](file:///d:/Resume/PharmaLens_Design.md)  

---

## 1. Executive Implementation Roadmap

This document outlines the sequential, engineering-grade implementation roadmap for **PharmaLens**. Each phase is engineered to be modular, verifiable, and strictly aligned with the architecture, engineering rules, and clinical editorial design system previously specified.

```
┌────────────────────────────────────────────────────────────────────────────────────────┐
│                                PHARMALENS BUILD ROADMAP                                │
├─────────────────┬─────────────────┬─────────────────┬─────────────────┬────────────────┤
│    PHASE 0      │     PHASE 1     │     PHASE 2     │     PHASE 3     │    PHASE 4     │
│   Workspace,    │ Database Layer, │ Document Parser │ LangGraph Multi-│ Frontend Shell,│
│  Toolchains &   │ Async Models &  │ & Supabase      │  Agent Pipeline │ Editorial Paper│
│ Cloud Storage   │ Template Seeds  │ File Storage    │  (4 AI Agents)  │  Design Tokens │
├─────────────────┼─────────────────┼─────────────────┼─────────────────┼────────────────┤
│    PHASE 5      │     PHASE 6     │     PHASE 7     │     PHASE 8     │    PHASE 9     │
│  Feature Pages  │ Polling Status  │ Audit Trails,   │ Realistic SOPs, │  Containerize, │
│ (Split Reader,  │ Engine, Async   │ Report Exports, │ Test Suites &   │ Cloud Deploy & │
│  Gap Scorecard) │ State & Alerts  │ Security Polish │ Seed Scenarios  │ Demo Package   │
└─────────────────┴─────────────────┴─────────────────┴─────────────────┴────────────────┘
```

---

## Phase 0: Workspace Scaffolding & Environment Initialization

### 0.1 Objective
Initialize the mono-repo layout, create isolated Python 3.11 virtual environment, initialize Node.js 18+ Vite project, and configure the Supabase Docker/CLI stack with persistent database and Storage volumes for local development and deployment.

### 0.2 Target Folder Structure
```
pharmalens/
├── pharmalens-backend/
│   ├── app/
│   │   ├── api/
│   │   ├── core/
│   │   ├── models/
│   │   ├── schemas/
│   │   ├── services/
│   │   ├── agents/
│   │   └── utils/
│   ├── alembic/
│   │   └── versions/
│   ├── alembic.ini
│   ├── requirements.txt
│   ├── .env
│   └── main.py
├── pharmalens-frontend/
│   ├── public/
│   ├── src/
│   │   ├── assets/
│   │   ├── components/
│   │   │   ├── layout/
│   │   │   ├── common/
│   │   │   ├── upload/
│   │   │   ├── report/
│   │   │   └── history/
│   │   ├── pages/
│   │   ├── services/
│   │   ├── hooks/
│   │   └── utils/
│   ├── index.html
│   ├── package.json
│   ├── vite.config.js
│   └── .env
├── docker-compose.yml
└── README.md
```

### 0.3 Tasks & Deliverables

1. **Root Directory & Git Setup**:
   - Initialize root directory `pharmalens/` with `.gitignore` covering Python cache/venvs, Node modules/builds, and `.env` files.
2. **Backend Setup (`pharmalens-backend`)**:
   - Create Python 3.11 virtual environment: `python -m venv venv`.
   - Write `requirements.txt` with pinned dependencies:
     ```txt
     fastapi==0.115.6
     uvicorn[standard]==0.30.6
     pydantic==2.10.5
     pydantic-settings==2.7.0
     sqlalchemy==2.0.36
     asyncpg==0.30.0
     alembic==1.14.1
     python-dotenv==1.1.0
     python-multipart==0.0.19
     PyPDF2==3.0.1
     pdfplumber==0.11.4
     python-docx==1.1.2
     langgraph==0.4.7
     langgraph-checkpoint==2.0.26
     langgraph-prebuilt==0.2.3
     langgraph-sdk==0.2.15
     langchain-core==0.3.86
     langchain-google-genai==2.1.4
     langchain-openai==0.3.4
     httpx==0.28.1
     ```
   - Create local `.env` for Supabase Docker:
     ```env
     SUPABASE_DB_URL=postgresql+asyncpg://postgres:postgres@127.0.0.1:54322/postgres
     SUPABASE_URL=http://127.0.0.1:54321
     SUPABASE_PUBLISHABLE_KEY=your-local-publishable-key
     STORAGE_BUCKET=pharmalens-docs
     STORAGE_TIMEOUT_SECONDS=120
     GOOGLE_API_KEY=your-google-gemini-key
     OPENAI_API_KEY=your-openai-key
     LLM_PROVIDER=google
     LLM_MAX_ATTEMPTS=2
     HOST=0.0.0.0
     PORT=8000
     CORS_ORIGINS=http://localhost:5173,http://127.0.0.1:5173
     LOG_LEVEL=INFO
     ```
3. **Frontend Setup (`pharmalens-frontend`)**:
   - Initialize React 18 with Vite: `npm create vite@latest . -- --template react`.
   - Install dependencies:
     ```bash
     npm install axios@1.7.9 lucide-react@0.469.0 react-router-dom@6.28.1
     ```
   - Configure `vite.config.js` with server proxy to FastAPI (`/api`).
   - Create `.env` with:
     ```env
     VITE_API_BASE_URL=http://localhost:8000
     ```
4. **Supabase Storage Bucket Provisioning**:
   - Initialize the local Supabase Storage service with `supabase start`, then create bucket `pharmalens-docs` in the Docker-backed project with allowed MIME types (`application/pdf`, `application/vnd.openxmlformats-officedocument.wordprocessingml.document`) and a 300MB limit. Persist the Storage volume in deployment.

### 0.4 Verification & Acceptance Criteria
- [ ] `python -c "import fastapi, pypdf2, pdfplumber, docx, langgraph; print('PharmaLens backend ready')"` completes without error.
- [ ] The local Supabase database and Storage bucket are verified with a simple test script.
- [ ] The Supabase Docker database and Storage bucket are verified with a simple deployment smoke test.
- [ ] `npm run build` runs cleanly in `pharmalens-frontend`.

---

## Phase 1: Database Layer, Async ORM Models & Regulatory Template Seeds

### 1.1 Objective
Construct the SQLAlchemy 2.0 async database schema in Supabase PostgreSQL, configure Alembic migrations for the Supabase Docker stack, and seed official pharmaceutical compliance templates (FDA 21 CFR Part 211, EU GMP Annex 1, and ICH Q10).

### 1.2 Target Files
- `pharmalens-backend/app/core/config.py`: Application settings from `.env`.
- `pharmalens-backend/app/core/database.py`: SQLAlchemy async engine and `get_db` session manager.
- `pharmalens-backend/app/models/base.py`: DeclarativeBase, UUID primary key mixin, timestamp mixins.
- `pharmalens-backend/app/models/document.py`: `Document` model.
- `pharmalens-backend/app/models/template.py`: `ComplianceTemplate`, `TemplateSection` models.
- `pharmalens-backend/app/models/analysis.py`: `Analysis`, `AnalysisGap`, `CorrectiveAction` models.
- `pharmalens-backend/app/models/audit.py`: `AuditLog` model (21 CFR Part 11).
- `pharmalens-backend/alembic/env.py`: Async Alembic migration environment.
- `pharmalens-backend/app/utils/seed_templates.py`: Regulatory template seed script.

### 1.3 Detailed Implementation Steps

1. **Async Session Management (`app/core/database.py`)**:
   - `create_async_engine(settings.database_url, pool_size=10, max_overflow=20, pool_pre_ping=True)` using `SUPABASE_DB_URL`.
   - `async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)`.
2. **Schema & Model Definitions**:
   - **`documents`**: `id (UUIDv4)`, `filename (VARCHAR 255)`, `file_type (pdf, docx)`, `file_size_bytes (BIGINT)`, `storage_path (VARCHAR 500)`, `extracted_text (TEXT)`, `uploaded_at (TIMESTAMPTZ)`.
   - **`compliance_templates`**: `id`, `name (VARCHAR 200)`, `version (VARCHAR 50)`, `description (TEXT)`, `governing_body (FDA, EMA, WHO, ICH)`, `created_at`.
   - **`template_sections`**: `id`, `template_id (FK)`, `section_code (VARCHAR 50, e.g., 211.67)`, `title (VARCHAR 255)`, `requirement_text (TEXT)`, `mandatory (BOOLEAN)`.
   - **`analyses`**: `id`, `document_id (FK)`, `template_id (FK)`, `status (pending, processing, completed, failed)`, `compliance_score (DECIMAL 5,2)`, `critical_gaps_count (INT)`, `major_gaps_count (INT)`, `minor_gaps_count (INT)`, `summary (TEXT)`, `error_message (TEXT)`, `started_at`, `completed_at`.
   - **`analysis_gaps`**: `id`, `analysis_id (FK)`, `template_section_id (FK)`, `severity (critical, major, minor)`, `document_excerpt (TEXT)`, `gap_description (TEXT)`, `remediation_guidance (TEXT)`.
   - **`corrective_actions`**: `id`, `analysis_gap_id (FK)`, `title (VARCHAR 255)`, `action_description (TEXT)`, `priority (immediate, short_term, long_term)`, `regulatory_reference (VARCHAR 100)`.
   - **`audit_logs`**: `id`, `entity_type`, `entity_id`, `action`, `metadata (JSONB)`, `timestamp`.
3. **Seed Standard Regulatory Frameworks (`seed_templates.py`)**:
   - **Template 1: FDA 21 CFR Part 211 (Current Good Manufacturing Practice for Finished Pharmaceuticals)**
     - *Sections*: § 211.22 (Quality control unit), § 211.67 (Equipment cleaning and maintenance), § 211.100 (Written procedures; deviations), § 211.113 (Control of microbiological contamination), § 211.160 (General laboratory controls), § 211.192 (Production record review).
   - **Template 2: EU GMP Annex 1 (Manufacture of Sterile Medicinal Products)**
     - *Sections*: Section 4 (Premises & Cleanroom Classification), Section 5 (Equipment & Sterilization), Section 9 (Environmental & Process Monitoring).
   - **Template 3: ICH Q10 (Pharmaceutical Quality System)**
     - *Sections*: Section 2 (Management Responsibility), Section 3 (Continual Improvement of Process Performance).

### 1.4 Verification & Acceptance Criteria
- [ ] Running `alembic upgrade head` creates all 7 tables in the local Supabase database without schema errors.
- [ ] Running `alembic upgrade head` also enables deny-by-default RLS on all public application tables and `alembic_version`.
- [ ] Running the same Docker deployment with persistent volumes preserves the schema and Storage objects.
- [ ] Running `python -m app.utils.seed_templates` seeds the 3 regulatory templates and the 11 normative sections listed above (6 FDA + 3 EU GMP + 2 ICH).
- [ ] Verified foreign keys and cascading behaviors in the Supabase Docker environment.

---

## Phase 2: Document Processing Engine, Supabase Storage & REST APIs

### 2.1 Objective
Build the document ingestion pipeline: multipart file upload handling, file type and size validation, text extraction (PyPDF2 with pdfplumber fallback and python-docx), an optional Dolphin-v2 layout-aware PDF parser, cloud storage integration with Supabase Storage, and REST API endpoints for document and template management.

### 2.2 Target Files
- `pharmalens-backend/app/services/storage_service.py`: Supabase Storage file uploader/downloader.
- `pharmalens-backend/app/services/document_processor.py`: Text extraction pipeline with fallback logic.
- `pharmalens-backend/app/services/dolphin_parser.py`: Optional lazy-loaded Dolphin-v2 PDF layout and element parser.
- `pharmalens-backend/app/schemas/document.py`: Pydantic upload and list schemas.
- `pharmalens-backend/app/schemas/template.py`: Template schemas.
- `pharmalens-backend/app/api/documents.py`: Document CRUD endpoints.
- `pharmalens-backend/app/api/templates.py`: Template retrieval endpoints.
- `pharmalens-backend/main.py`: Middleware, CORS, exception handlers.

### 2.3 Detailed Implementation Steps

1. **Document Processor Engine (`document_processor.py`)**:
   - Implement PDF extraction:
     ```python
     def extract_text_from_pdf(file_bytes: bytes) -> str:
         try:
             reader = PyPDF2.PdfReader(io.BytesIO(file_bytes))
             text = "\n".join([page.extract_text() or "" for page in reader.pages])
             if len(text.strip()) > 50:
                 return text
         except Exception:
             pass
         # Fallback to pdfplumber for complex multi-column layouts
         with pdfplumber.open(io.BytesIO(file_bytes)) as pdf:
             return "\n".join([page.extract_text() or "" for page in pdf.pages])
     ```
   - Implement DOCX extraction using `docx.Document(io.BytesIO(file_bytes))`.
   - Clean extracted text (remove NULL bytes, normalize UTF-8 whitespace).
2. **Storage Service (`storage_service.py`)**:
   - Use `httpx.AsyncClient` or Supabase Python SDK to upload raw file bytes to bucket `pharmalens-docs` at path `{document_uuid}.{ext}`.
   - Generate secure download/signed URLs for viewing.
3. **REST Endpoints (`api/documents.py`, `api/templates.py`)**:
   - `POST /api/documents`: Receives `UploadFile`. Validates extension (`.pdf`, `.docx`) and size (≤ 300MB). Runs extraction, uploads to storage, writes DB record, returns 201.
   - `GET /api/documents`: Returns list of uploaded documents with pagination and upload timestamps.
   - `GET /api/documents/{id}`: Returns document metadata and extracted text.
   - `DELETE /api/documents/{id}`: Deletes file from storage and cascades database records.
   - `GET /api/templates`: Returns available compliance templates.
   - `GET /api/templates/{id}`: Returns template including all regulatory sections.
4. **Optional Layout-Aware PDF Parsing**:
   - Keep `DOCUMENT_PARSER_PROVIDER=native` as the default so the backend does not require a heavyweight model.
   - In `auto` mode, attempt Dolphin-v2 only when native PDF text is empty or shorter than `DOLPHIN_NATIVE_TEXT_THRESHOLD`.
   - In `dolphin` mode, run Dolphin-v2 for PDFs and fall back to native extraction if its optional dependencies, model, memory, or inference are unavailable.
   - Render PDF pages in memory, preserve heading hierarchy and table Markdown, and store the resulting text in the existing `documents.extracted_text` column.
   - Run extraction in a worker thread so model inference does not block FastAPI's event loop.

### 2.4 Verification & Acceptance Criteria
- [ ] Uploading a 5-page sample SOP PDF extracts text completely and saves file to Supabase Storage.
- [ ] Uploading an unsupported file type (e.g. `.exe` or `.png`) returns `400 Bad Request` with clear rejection message.
- [ ] Uploading a file > 300MB returns `413 Payload Too Large`.
- [ ] With native extraction configured, the backend starts without Dolphin dependencies or model files.
- [ ] With `auto` or `dolphin` configured and a valid Dolphin-v2 runtime, a scanned PDF produces non-empty layout-aware text; if the runtime fails, upload still succeeds using the native fallback.

---

## Phase 3: LangGraph Multi-Agent Regulatory Compliance Pipeline

### 3.1 Objective
Implement the 4-agent sequential LangGraph pipeline: Document Section Extractor, Regulatory Framework Mapper, Gap Analyzer & Risk Classifier, and Corrective Action Recommender. Calculate the quantitative compliance score and persist structured findings.

### 3.2 Target Files
- `pharmalens-backend/app/agents/llm_config.py`: LLM factory (Gemini 1.5 Flash primary, GPT-4o-mini fallback).
- `pharmalens-backend/app/agents/schemas.py`: Pydantic structured output models.
- `pharmalens-backend/app/agents/document_parser_agent.py`: Agent 1 — Section breakdown.
- `pharmalens-backend/app/agents/regulatory_mapper_agent.py`: Agent 2 — Normative alignment.
- `pharmalens-backend/app/agents/gap_analyzer_agent.py`: Agent 3 — Gap & risk categorization.
- `pharmalens-backend/app/agents/corrective_action_agent.py`: Agent 4 — Actionable recommendations.
- `pharmalens-backend/app/agents/compliance_pipeline.py`: LangGraph `StateGraph` definition and execution harness.
- `pharmalens-backend/app/services/analysis_service.py`: Background job runner and result persistence.
- `pharmalens-backend/app/services/scoring.py`: Deterministic compliance-score calculator.
- `pharmalens-backend/app/api/analyses.py`: Analysis trigger, status polling, and report endpoints.

### 3.3 Detailed Implementation Steps

1. **Pipeline State Definition (`compliance_pipeline.py`)**:
   ```python
   class ComplianceState(TypedDict):
       document_id: str
       template_id: str
       document_text: str
       template_sections: list[dict]
       parsed_sections: list[dict]
       section_mappings: list[dict]
       gaps: list[dict]
       corrective_actions: list[dict]
       compliance_score: float
       summary: str
       error: str | None
   ```
2. **LangGraph StateGraph Nodes**:
   - **Node 1: Document Parser Agent**: Splits extracted text into structured logical sections (e.g. Purpose, Scope, Responsibilities, Cleaning Procedure, Deviation Handling, Record Retention).
   - **Node 2: Regulatory Mapper Agent**: Cross-references document sections against the chosen regulatory standard (e.g. FDA 21 CFR § 211.67) to determine coverage.
   - **Node 3: Gap Analyzer Agent**: Detects ambiguities, omissions, lack of objective criteria, or non-compliance. Classifies severity:
     - *Critical*: Direct regulatory violation risking product adulteration or sterility failure.
     - *Major*: Omission of mandatory procedure or quality unit sign-off.
     - *Minor*: Minor documentation ambiguity or formatting shortfall.
   - **Node 4: Corrective Action Recommender**: Formulates actionable remediation advice with priority (`immediate`, `short_term`, `long_term`).
3. **Quantitative Compliance Score Calculation**:
   - Algorithm:
     $$\text{Score} = \max\left(0, 100 - (\text{Critical} \times 25 + \text{Major} \times 10 + \text{Minor} \times 3)\right)$$
   - Categorization: 90-100% High Compliance, 70-89% Moderate Risk, <70% Critical Non-Compliance.
4. **Background Execution**:
   - `POST /api/analyses`: Creates `analyses` row with `status="processing"`, launches `asyncio.create_task(run_analysis_pipeline(analysis_id))`, and returns `202 Accepted`.
   - `GET /api/analyses/{id}`: Returns current status (`processing`, `completed`, `failed`), and when completed, returns full report with all gaps, excerpts, and corrective actions.
   - `GET /api/analyses`: Returns paginated analysis history with optional `document_id` and `status` filters.
   - Background workers use independent async database sessions, persist completion/failure audit events, and are cancelled before database-pool shutdown.

### 3.4 Verification & Acceptance Criteria
- [ ] Running the pipeline against a test SOP with deliberate gaps (e.g. missing cleaning validation limits) accurately flags the missing clause with `Critical` or `Major` severity.
- [x] The 4-agent graph runs sequentially from `START` to `END` without hanging or unhandled exceptions in the offline structured-model verification.
- [x] Compliance score correctly calculates and reflects the weighted gap count.

---

## Phase 4: Frontend Design System & Clinical Editorial Shell

### 4.1 Objective
Translate [PharmaLens_Design.md](file:///d:/Resume/PharmaLens_Design.md) into concrete Vanilla CSS design tokens, typography hierarchy (Maragsa display, Lato UI chrome, Arimo document reading body), clinical warm-paper color palette, and core layout components.

### 4.2 Target Files
- `pharmalens-frontend/src/index.css`: Global CSS custom properties (warm laboratory paper canvas `#FAFAF7`, clinical borders, editorial serif typography, severity tokens).
- `pharmalens-frontend/src/components/layout/Navbar.jsx`: Top navigation header with brand mark and route links.
- `pharmalens-frontend/src/components/layout/PageContainer.jsx`: Centered container with reading margins.
- `pharmalens-frontend/src/components/common/ScoreGauge.jsx`: Circular/bar compliance score indicator with color transitions.
- `pharmalens-frontend/src/components/common/SeverityBadge.jsx`: Triple-encoded badge (Critical Red, Major Orange, Minor Yellow).
- `pharmalens-frontend/src/components/common/StatCard.jsx`: Reusable metric card with subtle border and elevation.
- `pharmalens-frontend/src/components/common/LoadingSpinner.jsx`: Clinical pulse spinner.
- `pharmalens-frontend/src/App.jsx`: Route architecture.

### 4.3 Detailed Implementation Steps

1. **Design Tokens (`index.css`)**:
   - Google Font imports:
     ```css
     @import url('https://fonts.googleapis.com/css2?family=Arimo:ital,wght@0,400;0,500;0,600;0,700;1,400&family=Lato:ital,wght@0,300;0,400;0,700;0,900&family=Playfair+Display:ital,wght@0,600;0,700;1,600&display=swap');
     ```
   - Color variables for light theme (default):
     - Canvas Paper: `#FAFAF7`
     - Card Surface: `#FFFFFF`
     - Brand Red: `#C7372C`, Subtle Red: `rgba(199, 55, 44, 0.08)`
     - Compliant Green: `#457534`
     - Review Amber: `#F58F1F`
     - Text Primary: `#191211`, Text Secondary: `#5C5552`, Text Muted: `#8C8582`
     - Border Subdued: `#E8E5DF`, Border Medium: `#D4D0C8`
2. **Typography Rules**:
   - Display headings: High-contrast serif style (`Maragsa / Playfair Display`).
   - Interface controls, tables, buttons: `Lato`.
   - Document inspection viewer: `Arimo` (high readability for dense regulatory texts).
3. **Core Reusable Components**:
   - `ScoreGauge.jsx`: Visualizes 0-100% compliance with dynamic color matching (Green >= 90%, Amber 70-89%, Red < 70%).
   - `SeverityBadge.jsx`: Displays severity icon, text label, and non-color identifier for WCAG 2.1 AA accessibility.

### 4.4 Verification & Acceptance Criteria
- [ ] UI matches the warm clinical laboratory / regulatory reading room aesthetic in `PharmaLens_Design.md`.
- [ ] Font pairings render correctly (editorial display headers, clean UI controls, legible document text).
- [ ] Responsive layouts scale cleanly from 1440px desktop down to 768px tablet.

---

## Phase 5: Feature Modules & Page Implementations

### 5.1 Objective
Implement the 4 core product views: Executive Dashboard, Document Upload & Template Selector, Split-Screen Analysis Report, and Audit History Table.

### 5.2 Target Files & Modules

#### Module A: Overview Dashboard (`pages/Dashboard.jsx`)
- `components/dashboard/ComplianceStats.jsx`: 4 metric cards (Audited Documents, Avg Compliance Score, Open Critical Gaps, Remediated Findings).
- `components/dashboard/RecentAnalysesTable.jsx`: Interactive list of recent audits with quick-view report links.
- `components/dashboard/FrameworkBreakdown.jsx`: Breakdown of audits by framework (FDA vs EU GMP vs ICH).

#### Module B: Document Upload & Template Configuration (`pages/UploadPage.jsx`)
- `components/upload/FileDropZone.jsx`: Drag-and-drop zone with instant file validation, extension badge, and file size counter.
- `components/upload/TemplateSelector.jsx`: Dropdown selector pulling live templates from `GET /api/templates` with preview of sections.
- `components/upload/AnalysisTriggerButton.jsx`: Action button with loading state.

#### Module C: Split-Screen Analysis Report (`pages/AnalysisReport.jsx`)
- `components/report/ReportHeader.jsx`: Document title, timestamp, framework badge, print/export PDF button.
- `components/report/ScoreSummaryCard.jsx`: Quantitative score gauge, gap counters (Critical, Major, Minor), and executive summary text.
- `components/report/DocumentSplitViewer.jsx`: Two-column layout:
  - *Left Column (Document Reader)*: Renders extracted document text on white paper canvas with line numbers and highlighted findings.
  - *Right Column (Findings & Remediation Panel)*: Expandable list of `GapCard` items with corresponding regulatory references.
- `components/report/GapCard.jsx`: Card detailing gap, excerpt from document, regulatory citation, and nested `CorrectiveActionList`.
- `components/report/CorrectiveActionList.jsx`: Actionable remediation items categorized by priority.

#### Module D: Audit History & Archive (`pages/HistoryPage.jsx`)
- `components/history/HistoryTable.jsx`: Filterable, searchable table of all completed analyses with score badges and PDF download triggers.

### 5.3 Verification & Acceptance Criteria
- [ ] User can drop a file, pick FDA 21 CFR Part 211, and trigger analysis seamlessly.
- [ ] Clicking a finding card on the right highlights the corresponding excerpt in the document reader on the left.
- [ ] Report renders cleanly in both browser and browser print dialog (`Ctrl+P`).

---

## Phase 6: Asynchronous Polling, Analysis Progress & Status Feedback

### 6.1 Objective
Implement a smooth, resilient polling mechanism on the frontend to track the multi-agent AI execution, showing real-time stage progression without page refreshes.

### 6.2 Target Files
- `pharmalens-frontend/src/hooks/useAnalysisPolling.js`: Custom polling hook with exponential backoff.
- `pharmalens-frontend/src/components/upload/AnalysisProgressBar.jsx`: Multi-stage animated progress component.
- `pharmalens-frontend/src/components/common/ErrorBanner.jsx`: Recoverable error display with retry trigger.

### 6.3 Detailed Implementation Steps

1. **Multi-Stage Progress Visualizer (`AnalysisProgressBar.jsx`)**:
   - Step 1: Ingesting & Extracting Document Text
   - Step 2: Mapping Document Sections to Regulatory Framework
   - Step 3: Executing Deep Gap & Risk Analysis
   - Step 4: Formulating Corrective & Preventive Actions
   - Step 5: Assembling Final Compliance Scorecard
2. **Polling Hook Architecture (`useAnalysisPolling.js`)**:
   - Poll `GET /api/analyses/{id}` every 2 seconds.
   - If status is `processing`, update active step indicator.
   - If status is `completed`, stop polling and route user immediately to `/report/{id}`.
   - If status is `failed`, halt polling and render `ErrorBanner` with detailed error explanation and retry button.
   - Implement timeout (maximum 120 seconds) with fallback notice.

### 6.4 Verification & Acceptance Criteria
- [ ] After triggering analysis, the UI smoothly progresses through the visual pipeline stages.
- [ ] When analysis completes, browser automatically navigates to the detailed report view.
- [ ] If network is momentarily interrupted, polling recovers gracefully without breaking application state.

---

## Phase 7: Regulatory Compliance, Export Engine & Security Polish

### 7.1 Objective
Enforce 21 CFR Part 11 electronic records principles, implement high-resolution printable report styling, secure file handling, and verify WCAG 2.1 AA accessibility.

### 7.2 Implementation Details

1. **21 CFR Part 11 Electronic Records**:
   - Audit trail captures all actions: document upload, analysis trigger, report viewed, report exported.
   - Timestamps stored in UTC ISO-8601 with millisecond precision.
   - Records are non-destructive (deleting a document marks it as archived while preserving audit records).
2. **Print & Export CSS (`@media print`)**:
   - Dedicated print stylesheet hiding navigation bars, headers, and buttons.
   - Renders document title, compliance score, executive summary, and complete gap table formatted specifically for letter/A4 paper.
   - Adds formal regulatory header: *"PharmaLens Automated Regulatory Compliance Audit Report — Generated for Quality Assurance Review"*.
3. **Security & Input Sanitization**:
   - Verify uploaded file signatures (magic bytes) to prevent executable upload renaming.
   - Restrict Supabase database connections to asyncpg with parameterized ORM statements.
   - Rate limiting on analysis triggers to prevent LLM quota exhaustion.

### 7.3 Verification & Acceptance Criteria
- [ ] Print preview (`Ctrl+P`) produces an executive-ready multi-page PDF with zero cut-off text or broken margins.
- [ ] Uploading a renamed `.exe` file disguised as `.pdf` is rejected at the backend via magic byte verification.
- [ ] All audit logs verify integrity in Supabase SQL editor.

---

## Phase 8: Comprehensive Testing, Realistic Pharma SOPs & Seed Scenarios

### 8.1 Objective
Provide automated unit/integration tests and seed realistic pharmaceutical Standard Operating Procedures (SOPs) with known compliance gaps to allow instant, persuasive portfolio demonstrations.

### 8.2 Target Files
- `pharmalens-backend/tests/test_document_processor.py`: Tests for PDF/DOCX extraction.
- `pharmalens-backend/tests/test_compliance_pipeline.py`: Tests for LangGraph agent outputs.
- `pharmalens-backend/tests/test_api_endpoints.py`: Integration tests for FastAPI endpoints.
- `pharmalens-backend/app/utils/seed_demo_docs.py`: Script to generate realistic sample SOP files and pre-run analyses.

### 8.3 Realistic Test Documents to Include
1. **Document 1: SOP-QA-401 — Equipment Cleaning and Sanitization Procedure**:
   - *Framework*: FDA 21 CFR § 211.67 & EU GMP Annex 1.
   - *Injected Gaps*: Fails to specify maximum dirty holding time; lacks clear microbiological swab limit thresholds.
   - *Expected AI Output*: 1 Critical Gap, 1 Major Gap (Compliance Score ~65%).
2. **Document 2: SOP-PR-102 — Sterile Filling Suite Environmental Monitoring**:
   - *Framework*: EU GMP Annex 1 (2022 Revision).
   - *Injected Gaps*: Lacks continuous non-viable particle monitoring requirement in Grade A laminar flow zone.
   - *Expected AI Output*: 1 Critical Gap (Compliance Score ~75%).
3. **Document 3: SOP-QC-705 — Out of Specification (OOS) Investigation Protocol**:
   - *Framework*: FDA Guidance for Industry — Investigating OOS Test Results & ICH Q10.
   - *Expected AI Output*: Minor documentation wording improvements (Compliance Score ~94%).

### 8.4 Verification & Acceptance Criteria
- [ ] `pytest tests/` runs 15+ automated test cases with 100% pass rate.
- [ ] Running `python -m app.utils.seed_demo_docs` populates the dashboard with realistic audit reports ready for immediate presentation.

---

## Phase 9: Containerization, Deployment & Portfolio Presentation

### 9.1 Objective
Package PharmaLens and the self-hosted Supabase stack for zero-friction Docker deployment with persistent database and Storage volumes, then compile the interview walkthrough documentation.

### 9.2 Target Files
- `pharmalens/docker-compose.yml`: Multi-container configuration.
- `pharmalens/supabase/`: Supabase CLI/Docker configuration and persistent volume guidance.
- `pharmalens/pharmalens-backend/Dockerfile`: Python 3.11-slim container.
- `pharmalens/pharmalens-frontend/Dockerfile`: Vite multi-stage build.
- `pharmalens/README.md`: Architecture diagrams, API specs, and interview discussion topics.

### 9.3 Docker Compose Setup
```yaml
version: "3.8"
services:
  backend:
    build: ./pharmalens-backend
    ports:
      - "8000:8000"
    env_file: ./pharmalens-backend/.env
    restart: unless-stopped

  frontend:
    build: ./pharmalens-frontend
    ports:
      - "5173:80"
    depends_on:
      - backend
    restart: unless-stopped
```

### 9.4 Final Verification Checklist
- [ ] Running the Supabase Docker stack with persistent volumes launches PostgreSQL, Storage, API, and Studio.
- [ ] Running `docker compose up --build` launches backend and frontend against the Supabase stack.
- [ ] Restoring the Docker volumes recovers database rows and uploaded files.
- [ ] Dragging and dropping an SOP runs the entire 4-agent LangGraph pipeline in under 30 seconds.
- [ ] Split-screen reader and compliance scorecard render seamlessly.

---

> **End of PharmaLens Phase-by-Phase Implementation Plan.**  
> Ready for Phase 0 execution.
