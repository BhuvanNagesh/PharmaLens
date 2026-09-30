# PharmaLens — Rules & Guidelines Document

> **Project:** PharmaLens — AI-Powered Regulatory Compliance Copilot  
> **Author:** Bhuvan Nagesh  
> **Created:** 29-09-2026  
> **Purpose:** Definitive reference for what to use, what to avoid, how to handle errors, edge cases, boundaries, and coding standards during implementation.  

---

## 1. Technology Rules

### 1.1 What to Use

| Category | Use | Why |
|----------|-----|-----|
| **Python Runtime** | Python 3.11+ | Required for `asyncio` improvements and `typing` features |
| **Web Framework** | FastAPI with `async def` endpoints | All endpoints must be async for non-blocking I/O |
| **ORM** | SQLAlchemy 2.0 with async engine (`AsyncSession`) | Async DB queries prevent blocking the event loop |
| **DB Driver** | `asyncpg` | The only production-grade async PostgreSQL driver |
| **Migrations** | Alembic (autogenerate from SQLAlchemy models) | Schema version control; never modify DB schema manually |
| **Database** | Self-hosted Supabase PostgreSQL via Docker | Connect through `SUPABASE_DB_URL` |
| **File Storage** | Supabase Storage | Store original uploaded PDF/DOCX files |
| **LLM Orchestration** | LangGraph `StateGraph` | Stateful multi-agent pipeline with explicit state passing |
| **LLM Abstraction** | LangChain Core (`ChatPromptTemplate`, `StrOutputParser`) | Standardized LLM call interface |
| **LLM Provider** | `langchain-google-genai` (Gemini Flash) primary; `langchain-openai` (GPT-4o-mini) fallback | Cost-efficient; configurable via `LLM_PROVIDER` env var |
| **PDF Extraction** | `PyPDF2.PdfReader` with `pdfplumber` fallback; optional Dolphin-v2 provider | Native extraction is the default; Dolphin is opt-in for scanned or layout-heavy PDFs |
| **DOCX Extraction** | `python-docx` (`Document.paragraphs`) | Standard DOCX text extraction |
| **Validation** | Pydantic v2 `BaseModel` for all request/response schemas | Type-safe, auto-documented, serializable |
| **File Upload** | `python-multipart` with FastAPI `UploadFile` | Standard multipart/form-data handling |
| **Environment** | `python-dotenv` with `config.py` | Centralized env var loading; never hardcode secrets |
| **Logging** | Python `logging` module with structured format | No `print()` statements in production code |
| **UUID Generation** | `uuid.uuid4()` | All primary keys are UUIDs |
| **Timestamps** | `datetime.utcnow()` stored as `TIMESTAMP WITH TIME ZONE` | All timestamps in UTC |
| **HTTP Client** | `httpx` (async) | For Supabase Storage API calls |
| **Frontend** | React 18 + Vite 5 + React Router 6 | Standard SPA stack |
| **Frontend HTTP** | Axios with base URL from `VITE_API_BASE_URL` | Consistent API client |
| **Frontend Styling** | Vanilla CSS with CSS custom properties | No CSS frameworks; full control over design |
| **Frontend Icons** | Lucide React | Consistent, tree-shakeable icon library |

### 1.2 What NOT to Use

| Category | Avoid | Why |
|----------|-------|-----|
| **ORM** | Django ORM, Tortoise ORM, raw SQL strings | Project uses SQLAlchemy 2.0 async exclusively |
| **Web Framework** | Flask, Django | Project uses FastAPI exclusively |
| **Sync DB calls** | `create_engine()` (sync), `Session()` (sync) | Use `create_async_engine()` and `AsyncSession` only |
| **Database hardcoding** | Hardcoding a database host or silently falling back to another provider | Use the environment-backed `SUPABASE_DB_URL` |
| **Local File Storage** | Saving files to local filesystem (`/uploads/`) | Use Supabase Storage; local filesystem doesn't persist in cloud deployments |
| **LLM Direct Calls** | Raw `openai.ChatCompletion.create()` or `requests.post()` to LLM APIs | Use LangChain/LangGraph abstractions for consistency and retry logic |
| **Heavy LLM Models** | GPT-4, GPT-4-turbo, Claude, gemini-1.5-pro, or always-on vision models | Use GPT-4o-mini/Gemini Flash for compliance agents; Dolphin-v2 is an optional local document-parser add-on only |
| **Chart Libraries (FE)** | Chart.js, D3, Recharts | Not needed; use CSS-based stat cards |
| **CSS Frameworks (FE)** | TailwindCSS, Bootstrap, Material UI | Use vanilla CSS with design tokens |
| **State Management (FE)** | Redux, MobX, Zustand | React hooks + custom hooks are sufficient for this app's complexity |
| **TypeScript (FE)** | TypeScript | Use JavaScript (.jsx) to keep the stack simple and reduce setup time |
| **Testing Frameworks** | Jest, PyTest (for v1) | Focus on manual testing for initial build; add tests in v2 |
| **Auth** | JWT, OAuth, Supabase Auth | No authentication in v1; all endpoints are open |
| **print()** | `print()` for debugging | Use `logging.getLogger(__name__)` |
| **f-strings in SQL** | `f"SELECT * FROM {table}"` | Use SQLAlchemy ORM or parameterized queries; never interpolate SQL |

---

## 2. Library Versions (Pinned)

### Backend — `requirements.txt`

```
fastapi==0.115.6
uvicorn[standard]==0.30.6
sqlalchemy==2.0.36
asyncpg==0.30.0
alembic==1.14.1
python-multipart==0.0.19
pydantic==2.10.5
PyPDF2==3.0.1
pdfplumber==0.11.4
python-docx==1.1.2
langgraph==0.4.7
langgraph-checkpoint==2.0.26
langgraph-prebuilt==0.2.3
langgraph-sdk==0.2.15
langchain-core==0.3.86
langchain-openai==0.3.4
langchain-google-genai==2.1.4
python-dotenv==1.1.0
httpx==0.28.1
```

### Frontend — Key `package.json` Dependencies

```json
{
  "dependencies": {
    "react": "^18.3.1",
    "react-dom": "^18.3.1",
    "react-router-dom": "^6.28.0",
    "axios": "^1.7.9",
    "lucide-react": "^0.468.0"
  },
  "devDependencies": {
    "@vitejs/plugin-react": "^4.3.4",
    "vite": "^5.4.11"
  }
}
```

---

## 3. Coding Standards

### 3.1 Backend (Python)

| Rule | Standard |
|------|----------|
| **Naming** | `snake_case` for variables, functions, files; `PascalCase` for classes |
| **Async** | All endpoint handlers must be `async def`; all DB operations must use `await` |
| **Type Hints** | All function parameters and return types must have type hints |
| **Docstrings** | Every public function must have a one-line docstring |
| **Imports** | stdlib → third-party → local (separated by blank lines) |
| **Error Messages** | All user-facing error messages must be plain English (no stack traces) |
| **Config** | All configurable values must come from `config.py` → `.env` |
| **Models** | Every SQLAlchemy model must have `id = Column(UUID, primary_key=True, default=uuid4)` |
| **Schemas** | Every API endpoint must have a Pydantic `Request` and `Response` schema |
| **Dependencies** | Use FastAPI `Depends()` for DB session injection |
| **Router Prefix** | All routers must use `/api/` prefix |
| **HTTP Status Codes** | 200 OK, 201 Created, 202 Accepted, 400 Bad Request, 404 Not Found, 422 Validation Error, 500 Internal Server Error |

### 3.2 Frontend (JavaScript/React)

| Rule | Standard |
|------|----------|
| **Naming** | `camelCase` for variables/functions; `PascalCase` for components |
| **Components** | One component per file; file name matches component name |
| **Hooks** | Custom hooks prefixed with `use` (e.g., `useDocuments`) |
| **API Calls** | All API calls go through `services/api.js`; components never call `axios` directly |
| **Error Handling** | Every API call must have `.catch()` with user-friendly error display |
| **Loading States** | Every page/component that fetches data must show `<LoadingSpinner />` while loading |
| **Empty States** | Every list/collection must show `<EmptyState />` when empty |
| **CSS** | Use CSS custom properties (variables) from `App.css`; no inline styles |
| **File Extensions** | `.jsx` for React components; `.js` for utilities/services/hooks |

---

## 4. Application Boundaries & Scope

### 4.1 In Scope (v1)

| Feature | Status |
|---------|--------|
| Document upload (PDF + DOCX) with text extraction | ✅ Build |
| Compliance template CRUD (create, read, update, delete) | ✅ Build |
| LangGraph 4-agent compliance analysis pipeline | ✅ Build |
| Analysis report with gaps and corrective actions | ✅ Build |
| Analysis history with filtering | ✅ Build |
| Audit trail logging | ✅ Build |
| React SPA with 4 pages | ✅ Build |
| Self-hosted Supabase PostgreSQL Docker stack for data persistence | ✅ Build |
| Supabase Storage for file persistence | ✅ Build |
| CORS configuration for frontend access | ✅ Build |

### 4.2 Out of Scope (NOT in v1)

| Feature | Why |
|---------|-----|
| User authentication (login/signup) | Adds complexity without demonstrating core AI/workflow skills |
| Role-based access control (RBAC) | Requires auth first |
| Multi-tenancy | Single-user portfolio project |
| Always-on OCR for every upload | Expensive heavyweight parsing is not required for the core path; optional Dolphin-v2 handles scanned PDFs only when explicitly configured |
| Real-time WebSocket updates | PharmaLens uses polling (not WebSocket); DeviationFlow has WS |
| PDF report generation/download | Frontend can screenshot; not core |
| Email notifications | Requires email service integration |
| Internationalization (i18n) | English only |
| Dark mode | Nice-to-have; not in v1 |
| Mobile responsiveness below 768px | Desktop + tablet only |
| Unit tests / integration tests | Manual testing in v1; add in v2 |
| CI/CD pipeline | Manual deployment in v1 |
| Rate limiting | Not needed at project scale |
| Caching | Not needed; PostgreSQL queries are sufficient at project scale |

---

## 5. Edge Cases & How to Handle Them

### 5.1 Document Processing Edge Cases

| Edge Case | How to Handle |
|-----------|--------------|
| **PDF with scanned images (no extractable text)** | `native` mode stores empty text; `auto` or `dolphin` mode attempts optional Dolphin-v2 layout parsing and falls back to empty native text if the optional runtime is unavailable |
| **Corrupted PDF that cannot be read** | Catch `PyPDF2.errors.PdfReadError` or `Exception` → return 400 `"Unable to process this file. The document may be corrupted"` |
| **Empty DOCX (no paragraphs)** | `extracted_text = ""` → same behavior as scanned PDF |
| **Very large document (100+ pages)** | Text extraction succeeds normally → if extracted text exceeds LLM context window, Agent 1 truncates to first ~100K characters and processes what fits → note truncation in agent output |
| **File with wrong extension** | Validate extension in router → 400 `"Unsupported file type. Only PDF and DOCX files are accepted"` |
| **File exceeds 300 MB** | Check `file.size` in router → 413 `"File size exceeds 300MB limit"` |
| **Upload with no file** | FastAPI `UploadFile` validation → 400 `"No file uploaded"` |
| **Duplicate filename** | Allowed; each upload gets a unique UUID → no filename collision |
| **Special characters in filename** | Store original filename as-is in DB; use UUID for storage path |
| **Oversized or control-character filename** | Reject filenames longer than 255 characters or containing control characters before Storage or database writes |
| **Concurrent uploads** | Each upload creates independent records; no conflict |

### 5.2 LangGraph Pipeline Edge Cases

| Edge Case | How to Handle |
|-----------|--------------|
| **LLM API timeout (>30s)** | Catch timeout exception → set analysis `status = "failed"` → log error in audit trail → return analysis with `status: "failed"` when polled |
| **LLM returns malformed JSON** | Catch `json.JSONDecodeError` → retry once with clarification prompt ("Please return valid JSON matching this schema: ...") → if still fails, set `status = "failed"` |
| **LLM rate limit (429)** | Exponential backoff: wait 1s → 2s → 4s (3 retries max) → if exhausted, set `status = "failed"` |
| **LLM returns unexpected enum values** | Validate against allowed enums (severity must be "critical"/"major"/"minor") → if invalid, fall back to "minor" and log warning |
| **Template with 0 matching sections** | All template sections classified as "missing" → all gaps = "critical" → valid analysis |
| **Agent 1 finds 0 sections in document** | All template sections unmatched → Agent 3 generates gaps for all required sections |
| **Agent produces empty output** | Treat as pipeline failure → set `status = "failed"` → log in audit trail |
| **LLM provider API is down entirely** | After retries fail, set `status = "failed"` → frontend shows error with "Try Again" button |

### 5.3 API Edge Cases

| Edge Case | How to Handle |
|-----------|--------------|
| **GET analysis while still "processing"** | Return current analysis record with `status: "processing"` and empty `gaps[]` / `corrective_actions[]` |
| **DELETE document with associated analyses** | Cascade delete: `analyses` → `analysis_gaps` → `corrective_actions` → `audit_logs` (where entity_type = "analysis") |
| **Trigger analysis with non-existent document_id** | Validate → 404 `"Document not found"` |
| **Trigger analysis with non-existent template_id** | Validate → 404 `"Compliance template not found"` |
| **Duplicate analysis (same document + template)** | Allowed; creates a new analysis record (enables comparison) |
| **Concurrent analyses on same document** | Both succeed independently; each creates separate records |
| **Create template with 0 sections** | Pydantic validation → 422 `"Template must have at least one required section"` |
| **Create template with duplicate section names** | Allowed; not enforced at DB level (sections are ordered by `order_index`) |
| **Invalid UUID in path parameters** | Pydantic UUID validation → 422 `"Invalid ID format"` |
| **Pagination: page=0 or negative** | Validate → 422 `"Page must be a positive integer"` |
| **Pagination: limit > 100** | Cap at 100 → return max 100 results |

### 5.4 Database Edge Cases

| Edge Case | How to Handle |
|-----------|--------------|
| **UUID collision** | Statistically negligible (~1 in 2^122); handled by PK constraint |
| **Very long extracted text (>1MB)** | PostgreSQL `TEXT` type has no practical limit; store as-is |
| **Null extracted_text** | Set to empty string `""`, never NULL |
| **Database connection failure** | Catch `asyncpg.ConnectionError` → return 500 → log the selected database target without logging credentials |
| **Supabase Storage upload failure** | Catch the Storage exception → roll back the database transaction → return a safe 500 response; never create a document row without its original file |
| **Concurrent writes** | SQLAlchemy async handles connection pooling; no explicit locking needed at this scale |

### 5.5 Frontend Edge Cases

| Edge Case | How to Handle |
|-----------|--------------|
| **API server unreachable** | Axios timeout (10s) → show `<ErrorBanner>` with message "Unable to connect to server" and retry button |
| **Analysis polling timeout** | Stop polling after 120 seconds (40 polls at 3s interval) → show "Analysis is taking longer than expected. Please check back later." |
| **Empty template list** | TemplateSelector shows `<EmptyState>` with "No templates found. Create one first." |
| **No documents uploaded yet** | Dashboard shows `<EmptyState>` with "Upload your first document to get started." |
| **Browser refresh during polling** | React Router remounts AnalysisProgress → resume polling from GET /api/analyses/:id |
| **Very long gap description** | CSS `word-break: break-word` on GapCard; no truncation |
| **Large number of gaps (20+)** | All gaps rendered; consider pagination in v2 |

---

## 6. Error Handling

### 6.1 Backend Error Response Format

All errors must return JSON with a `detail` field:

```python
from fastapi import HTTPException

# Standard error response
raise HTTPException(status_code=404, detail="Document not found")

# Pydantic validation errors are auto-handled by FastAPI (422 response)
```

### 6.2 Error Catalogue

| HTTP Code | Scenario | Response Body |
|-----------|----------|---------------|
| **400** | No file in upload request | `{ "detail": "No file uploaded" }` |
| **400** | Unsupported file type | `{ "detail": "Unsupported file type. Only PDF and DOCX files are accepted" }` |
| **413** | File too large (>300MB) | `{ "detail": "File size exceeds 300MB limit" }` |
| **400** | Corrupted file | `{ "detail": "Unable to process this file. The document may be corrupted" }` |
| **404** | Document not found | `{ "detail": "Document not found" }` |
| **404** | Template not found | `{ "detail": "Compliance template not found" }` |
| **404** | Analysis not found | `{ "detail": "Analysis not found" }` |
| **422** | Invalid UUID format | `{ "detail": "Invalid ID format" }` |
| **422** | Missing required field | Pydantic auto-response with field-level error details |
| **422** | Template with 0 sections | `{ "detail": "Template must have at least one required section" }` |
| **422** | Page must be positive | `{ "detail": "Page must be a positive integer" }` |
| **500** | Internal server error | `{ "detail": "Internal server error" }` (logged to console) |
| **500** | Database connection failure | `{ "detail": "Internal server error" }` (logged with DB error details) |

### 6.3 LLM Failure Handling

```python
# Pattern for all LangGraph agent nodes
async def agent_node(state: ComplianceState) -> ComplianceState:
    try:
        response = await llm.ainvoke(prompt)
        parsed = json.loads(response.content)
        # Validate against expected schema
        state["output_field"] = parsed
    except json.JSONDecodeError:
        # Retry once with clarification
        try:
            response = await llm.ainvoke(retry_prompt)
            parsed = json.loads(response.content)
            state["output_field"] = parsed
        except Exception:
            state["output_field"] = []  # Empty output
            state["metadata"]["error"] = "Agent failed to produce valid output"
    except Exception as e:
        logger.error(f"Agent failed: {e}")
        state["output_field"] = []
        state["metadata"]["error"] = str(e)
    return state
```

### 6.4 Global Exception Handler

```python
# main.py
from fastapi import Request
from fastapi.responses import JSONResponse

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"}
    )
```

### 6.5 Frontend Error Handling

```javascript
// services/api.js — Axios interceptor
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response) {
      // Server responded with error status
      const message = error.response.data?.detail || "Something went wrong";
      return Promise.reject(new Error(message));
    } else if (error.request) {
      // No response received (network error)
      return Promise.reject(new Error("Unable to connect to server. Please check your connection."));
    } else {
      return Promise.reject(new Error("An unexpected error occurred."));
    }
  }
);
```

---

## 7. API Design Rules

| Rule | Standard |
|------|----------|
| All endpoints must be prefixed with `/api/` | `/api/documents`, `/api/analyses`, `/api/templates` |
| Use plural nouns for resource names | `/api/documents` (not `/api/document`) |
| Use UUID for resource IDs | `GET /api/documents/550e8400-e29b-41d4-a716-446655440000` |
| Use query parameters for filtering | `GET /api/analyses?document_id=xxx&status=completed` |
| Use query parameters for pagination | `?page=1&limit=10` (defaults: page=1, limit=10, max limit=100) |
| POST returns 201 for creation | `POST /api/documents` → 201 |
| POST returns 202 for async operations | `POST /api/analyses` → 202 (processing started) |
| DELETE returns 204 (no content) | `DELETE /api/documents/:id` → 204 |
| Use snake_case in JSON keys | `{ "document_id": "...", "file_type": "pdf" }` |
| All responses must be JSON | Content-Type: application/json |
| All timestamps in ISO 8601 UTC | `"2026-09-28T14:00:00Z"` |

---

## 8. Database Rules

| Rule | Standard |
|------|----------|
| All tables use UUID primary keys | `id = Column(UUID, primary_key=True, default=uuid4)` |
| All tables have `created_at` timestamp | `created_at = Column(DateTime(timezone=True), default=datetime.utcnow)` |
| Foreign keys use `ondelete="CASCADE"` where parent deletion should cascade | documents → analyses → analysis_gaps → corrective_actions |
| Use `TEXT` for long strings, `VARCHAR(N)` for bounded strings | `description = Column(Text)`, `filename = Column(String(255))` |
| Use `JSONB` for semi-structured data | `details = Column(JSONB)` in audit_logs |
| Never store secrets in the database | API keys, passwords → `.env` only |
| Use Alembic for all schema changes | Never run raw `ALTER TABLE` on Supabase |
| Supabase Docker persistence | Run migrations against the Supabase Docker database and persist its database/Storage volumes; never dual-write to another database |
| RLS migration | Run `alembic upgrade head`; migration `002_enable_public_rls` enables deny-by-default RLS on all application tables and `alembic_version` |
| Null values | Only use NULL where absence has semantic meaning (e.g., `completed_at` before completion); use empty string for text fields |
| Index foreign keys | All FK columns must have a B-tree index |

---

## 9. Security Rules

| Rule | Details |
|------|---------|
| **No auth in v1** | All endpoints are open; add JWT auth in v2 |
| **CORS** | Whitelist `CORS_ORIGINS` from `.env`; never use `allow_origins=["*"]` in production |
| **No secrets in code** | All API keys, DB URLs, and credentials must be in `.env` (git-ignored) |
| **File validation** | Validate file extension AND content-type header on upload |
| **File size limit** | 300 MB max per upload; enforced in router |
| **SQL injection** | Use SQLAlchemy ORM exclusively; never construct SQL strings |
| **Input sanitization** | Pydantic handles type validation; strip leading/trailing whitespace on text fields |
| **Environment files** | Keep the real `.env` local and ignored; never commit credentials or create duplicate environment templates with secrets |
| **Supabase keys** | Use the publishable/anon key (not a `service_role`/secret key) for Storage operations |
| **Public database tables** | Enable RLS on every table exposed in the `public` schema; create no `anon` or `authenticated` table policies in v1. The FastAPI database connection remains the trusted server-side path. |

---

## 10. Git & Version Control Rules

| Rule | Standard |
|------|----------|
| **Branch strategy** | `main` (production-ready) + `dev` (active development) |
| **Commit messages** | `feat: add document upload endpoint`, `fix: handle corrupted PDF`, `refactor: extract PDF processor` |
| **.gitignore** | Include: `venv/`, `node_modules/`, `.env`, `__pycache__/`, `*.pyc`, `alembic/versions/*.pyc` |
| **No large files** | Never commit PDFs, DOCX files, or uploaded test documents to Git |
| **No secrets** | Never commit `.env`, API keys, or database URLs |

---

## 11. Performance Guidelines

| Area | Guideline |
|------|-----------|
| **DB Queries** | Use `select()` with specific columns when loading lists (not `SELECT *`) |
| **Pagination** | Always paginate list endpoints; default limit=10, max=100 |
| **LLM Calls** | Use async `ainvoke()` for all LLM calls; don't block the event loop |
| **Connection Pool** | SQLAlchemy async engine manages connection pooling automatically; max pool size = 5 (default) |
| **File Processing** | Read uploaded files into memory (max 300MB); don't stream to disk |
| **Frontend Polling** | Poll every 3 seconds during analysis; stop after 120 seconds |
| **Frontend Re-renders** | Use React `useCallback` and `useMemo` for expensive computations |
| **API Timeout** | Axios timeout = 10 seconds for standard calls; 60 seconds for analysis trigger |

---
