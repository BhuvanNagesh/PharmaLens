# PharmaLens Backend

The PharmaLens backend is a FastAPI service for uploading pharmaceutical compliance documents, extracting document content, managing regulatory templates, and running asynchronous compliance analysis.

This guide is for using the backend locally and preparing it for deployment. Run backend commands from this directory unless a section explicitly says to move to the repository root.

## What the backend does

The service provides:

- PDF and DOCX upload with a 300 MiB per-file limit.
- PDF/DOCX signature and MIME validation.
- Native text extraction, including DOCX tables.
- Optional Dolphin-v2 layout-aware parsing.
- Private Supabase Storage integration through the `pharmalens-docs` bucket.
- Compliance-template CRUD operations.
- A four-agent LangGraph analysis workflow.
- Deterministic compliance scoring from persisted gap severities.
- Background processing with status polling.
- Recovery of interrupted analyses during application startup.
- Audit-log persistence for document, template, and analysis events.

The backend uses Supabase PostgreSQL and Supabase Storage. It does not use MongoDB or a separate standalone PostgreSQL installation.

## Backend structure

```text
pharmalens-backend/
├── app/
│   ├── agents/              # LangGraph state, nodes, and LLM providers
│   ├── api/                 # FastAPI route handlers
│   ├── core/                # Settings, database, and shared dependencies
│   ├── models/              # SQLAlchemy ORM models
│   ├── schemas/             # Pydantic request and response models
│   ├── services/            # Storage, extraction, scoring, and analysis
│   └── utils/               # Seed and maintenance utilities
├── alembic/
│   ├── env.py
│   └── versions/
│       ├── 001_initial_schema.py
│       └── 002_enable_public_rls.py
├── main.py                  # FastAPI application entry point
├── requirements.txt         # Core runtime dependencies
├── requirements-dolphin.txt # Optional Dolphin dependencies
├── .env                     # Local configuration; never commit
└── README.md
```

## Requirements

- Python 3.11 or newer.
- Docker Desktop running the local Supabase stack, or a reachable Supabase project.
- Node.js with `npx` when starting Supabase locally.
- A Google API key when `LLM_PROVIDER=google`.
- An OpenAI API key when `LLM_PROVIDER=openai`, or as a configured fallback.
- Optional Dolphin-v2 runtime, dependencies, and model weights for layout-aware parsing.

## Quick start

### 1. Start Supabase locally

Run this from the repository root, one directory above this backend directory:

```powershell
cd D:\Resume\PharmaLens
npx supabase start
npx supabase status
```

The local services normally use:

```text
Supabase API:    http://127.0.0.1:54321
PostgreSQL:      127.0.0.1:54322
Supabase Studio: http://127.0.0.1:54323
```

If you use Supabase Cloud instead, skip the local Docker commands and use the project URL, publishable key, and PostgreSQL connection string from the Cloud dashboard.

### 2. Create the Python environment

```powershell
cd D:\Resume\PharmaLens\pharmalens-backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
```

For macOS or Linux, activate the environment with:

```bash
source .venv/bin/activate
```

### 3. Configure `.env`

Create `pharmalens-backend\.env`. The application reads this file automatically from the backend directory.

```dotenv
SUPABASE_URL=http://127.0.0.1:54321
SUPABASE_PUBLISHABLE_KEY=copy-the-publishable-key-from-supabase-status
SUPABASE_DB_URL=postgresql+asyncpg://postgres:postgres@127.0.0.1:54322/postgres
STORAGE_BUCKET=pharmalens-docs
STORAGE_TIMEOUT_SECONDS=120

GOOGLE_API_KEY=your-google-api-key
OPENAI_API_KEY=optional-openai-api-key
LLM_PROVIDER=google
LLM_MAX_ATTEMPTS=2

DOCUMENT_PARSER_PROVIDER=native
DOLPHIN_MODEL_PATH=
DOLPHIN_DEVICE=auto
DOLPHIN_MAX_PAGES=100
DOLPHIN_MAX_NEW_TOKENS=4096
DOLPHIN_NATIVE_TEXT_THRESHOLD=50

HOST=0.0.0.0
PORT=8000
CORS_ORIGINS=http://localhost:5173,http://127.0.0.1:5173
LOG_LEVEL=INFO
```

For a hosted Supabase project, replace the local values for `SUPABASE_URL`, `SUPABASE_PUBLISHABLE_KEY`, and `SUPABASE_DB_URL`. Keep the variable names unchanged.

The names above are configuration examples, not credentials. Never commit `.env`, database passwords, Supabase keys, or LLM keys. Rotate any credential that has been exposed in a chat, screenshot, terminal recording, or repository.

### 4. Apply migrations and seed templates

With the virtual environment active and `.env` configured:

```powershell
cd D:\Resume\PharmaLens\pharmalens-backend
alembic upgrade head
python -m app.utils.seed_templates
```

The migrations create the application schema and enable row-level security on the public application tables. The current head is `002_enable_public_rls`.

The seed command creates the bundled compliance templates and sections. Run it only when the environment needs the bundled seed data.

### 5. Start the API

```powershell
cd D:\Resume\PharmaLens\pharmalens-backend
.\.venv\Scripts\Activate.ps1
python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

The API is then available at:

```text
http://127.0.0.1:8000
```

Interactive API documentation is available at:

```text
Swagger UI: http://127.0.0.1:8000/docs
ReDoc:      http://127.0.0.1:8000/redoc
```

## Verify that the backend is running

PowerShell:

```powershell
Invoke-RestMethod http://127.0.0.1:8000/api/health
```

Expected response shape:

```json
{
  "status": "ok"
}
```

If the request fails, confirm that the Uvicorn process is running, the port is available, and the database and Supabase Storage settings are valid.

## How to use the API

The examples below use `http://127.0.0.1:8000`. Replace that base URL when the API is deployed elsewhere.

### List seeded templates

```powershell
Invoke-RestMethod "http://127.0.0.1:8000/api/templates?page=1&limit=10"
```

Copy one returned template `id`. It is required to start an analysis.

### Create a compliance template

```powershell
$templateBody = @{
  name = "Example GMP Review"
  version = "2026.1"
  description = "Internal review template for GMP documentation"
  governing_body = "FDA"
  sections = @(
    @{
      section_code = "gmp-001"
      title = "Quality Management System"
      requirement_text = "The document must describe the quality management responsibilities and controls."
      mandatory = $true
      order_index = 1
    },
    @{
      section_code = "gmp-002"
      title = "Documentation Controls"
      requirement_text = "The document must define document approval, revision, and retention controls."
      mandatory = $true
      order_index = 2
    }
  )
} | ConvertTo-Json -Depth 5

Invoke-RestMethod `
  -Method Post `
  -Uri "http://127.0.0.1:8000/api/templates" `
  -ContentType "application/json" `
  -Body $templateBody
```

Supported canonical `governing_body` values are `FDA`, `EMA`, `WHO`, and `ICH`. The API also accepts the older `framework`, `section_name`, `description`, and `is_mandatory` request names for compatibility, but new clients should use the canonical names shown above.

### Upload a PDF or DOCX document

Use `curl.exe` from PowerShell for multipart upload:

```powershell
curl.exe -X POST "http://127.0.0.1:8000/api/documents" `
  -F "file=@C:\path\to\document.pdf;type=application/pdf"
```

For DOCX:

```powershell
curl.exe -X POST "http://127.0.0.1:8000/api/documents" `
  -F "file=@C:\path\to\document.docx;type=application/vnd.openxmlformats-officedocument.wordprocessingml.document"
```

The upload response contains the generated document `id`. Save it for the analysis request.

Upload rules:

- Accepted extensions are `.pdf` and `.docx`.
- The declared MIME type must match the extension.
- The content signature must match the claimed file type.
- Empty files and corrupted files are rejected.
- The maximum file size is 300 MiB.

### List uploaded documents

```powershell
Invoke-RestMethod "http://127.0.0.1:8000/api/documents?page=1&limit=10"
```

### Retrieve one document and its extracted text

```powershell
$documentId = "document-uuid-from-upload-response"
Invoke-RestMethod "http://127.0.0.1:8000/api/documents/$documentId"
```

### Start a compliance analysis

The analysis runs in the background. It requires an uploaded document ID and a template ID.

```powershell
$analysisBody = @{
  document_id = "document-uuid-from-upload-response"
  template_id = "template-uuid-from-template-list"
} | ConvertTo-Json

$accepted = Invoke-RestMethod `
  -Method Post `
  -Uri "http://127.0.0.1:8000/api/analyses" `
  -ContentType "application/json" `
  -Body $analysisBody

$accepted
```

The response includes `analysis_id` and normally has status `processing`.

### Poll analysis status and retrieve the report

```powershell
$analysisId = $accepted.analysis_id

do {
  $report = Invoke-RestMethod "http://127.0.0.1:8000/api/analyses/$analysisId"
  $report.status
  if ($report.status -in @("pending", "processing")) {
    Start-Sleep -Seconds 3
  }
} while ($report.status -in @("pending", "processing"))

$report | ConvertTo-Json -Depth 10
```

When the status is `completed`, the response contains the compliance score, summary, gaps, and corrective actions. When the status is `failed`, inspect the backend logs and the returned safe `error_message`.

### List analysis history

```powershell
Invoke-RestMethod "http://127.0.0.1:8000/api/analyses?page=1&limit=10"
```

Filter by document or status:

```powershell
Invoke-RestMethod "http://127.0.0.1:8000/api/analyses?document_id=$documentId&status=completed&page=1&limit=10"
```

Supported statuses are `pending`, `processing`, `completed`, and `failed`.

### Delete a document

```powershell
Invoke-RestMethod `
  -Method Delete `
  -Uri "http://127.0.0.1:8000/api/documents/$documentId"
```

Deletion removes the original from Supabase Storage and deletes the document record with its cascaded analysis data. The endpoint returns HTTP `204` on success.

### Delete a template

```powershell
$templateId = "template-uuid"
Invoke-RestMethod `
  -Method Delete `
  -Uri "http://127.0.0.1:8000/api/templates/$templateId"
```

A template referenced by an analysis cannot be deleted. Create a replacement or retain the existing template instead.

## Analysis behavior

The background pipeline runs these stages in order:

```text
document parser
      -> regulatory mapper
      -> gap analyzer
      -> corrective-action recommender
      -> deterministic score calculation
```

The LLM produces structured sections, mappings, gaps, and corrective actions. The backend validates those relationships before persisting a completed report. Every gap must map to a real template section and include at least one corrective action.

The score is calculated without an additional LLM call:

```text
score = max(0, 100 - (critical_gaps * 25) - (major_gaps * 10) - (minor_gaps * 3))
```

If the API process restarts while an analysis is processing, startup recovery marks the interrupted analysis as failed with a safe message. A new analysis can then be submitted normally.

## Environment variables

| Variable | Required | Purpose |
| --- | --- | --- |
| `SUPABASE_URL` | Yes | Supabase API URL used by Storage |
| `SUPABASE_PUBLISHABLE_KEY` | Yes | Publishable key used for Storage requests |
| `SUPABASE_DB_URL` | Yes | SQLAlchemy async PostgreSQL connection string |
| `STORAGE_BUCKET` | Yes | Storage bucket; use `pharmalens-docs` |
| `STORAGE_TIMEOUT_SECONDS` | No | Storage request timeout from 10 to 600 seconds; default `120` |
| `GOOGLE_API_KEY` | Provider-dependent | Gemini credentials when `LLM_PROVIDER=google` |
| `OPENAI_API_KEY` | Provider-dependent | OpenAI credentials when `LLM_PROVIDER=openai` or used as fallback |
| `LLM_PROVIDER` | No | Primary provider; default `google` |
| `LLM_MAX_ATTEMPTS` | No | Same-provider retry attempts from 1 to 3; default `2` |
| `DOCUMENT_PARSER_PROVIDER` | No | `native`, `auto`, or `dolphin`; default `native` |
| `DOLPHIN_MODEL_PATH` | Dolphin only | Local Dolphin model directory or identifier |
| `DOLPHIN_DEVICE` | No | Dolphin device selection; default `auto` |
| `DOLPHIN_MAX_PAGES` | No | Maximum pages for Dolphin parsing; default `100` |
| `DOLPHIN_MAX_NEW_TOKENS` | No | Dolphin generation limit; default `4096` |
| `DOLPHIN_NATIVE_TEXT_THRESHOLD` | No | Native-text threshold used by `auto`; default `50` |
| `HOST` | No | Uvicorn host; default `0.0.0.0` |
| `PORT` | No | Uvicorn port; default `8000` |
| `CORS_ORIGINS` | No | Comma-separated allowed frontend origins |
| `LOG_LEVEL` | No | Logging level; default `INFO` |

The application loads `.env` from the backend directory. Environment variables supplied by the process environment can override values according to the Pydantic Settings configuration.

## Document parser modes

### `native`

Uses the built-in PDF and DOCX extraction path. This is the default and does not require Dolphin model weights.

### `auto`

Runs native extraction first. It attempts Dolphin for PDFs where native extraction returns empty or very short text, then falls back to native output if Dolphin is unavailable or fails.

### `dolphin`

Attempts Dolphin parsing first and falls back to native extraction when the optional runtime is unavailable or returns an error.

Install optional dependencies with:

```powershell
pip install -r requirements-dolphin.txt
```

Model weights are not distributed with this repository.

## Database and Storage operations

Run migrations against the database configured in `SUPABASE_DB_URL`:

```powershell
alembic upgrade head
alembic current
alembic history
```

To create a new migration during development:

```powershell
alembic revision -m "describe the schema change"
```

The current migrations enable RLS on the public application tables. The RLS migration intentionally does not create broad public table policies. The backend accesses PostgreSQL through its trusted database connection.

Storage uses the private `pharmalens-docs` bucket with PDF/DOCX MIME restrictions and a 300 MiB limit. Storage policy SQL is maintained in the repository-level `supabase/migrations/20260930000000_storage_policies.sql` file.

## Verification and development checks

Run these commands from this directory:

```powershell
python -m compileall -q app main.py alembic
alembic history
```

Before an API change is considered complete, verify at least:

1. `/api/health` responds.
2. Template listing and validation work.
3. A valid PDF and DOCX upload successfully.
4. An empty, malformed, unsupported, or oversized upload is rejected.
5. An analysis can be queued and reaches `completed` or `failed` safely.
6. A document deletion removes both database metadata and Storage content.
7. The RLS migration is applied to the target database.

The repository currently relies on these compilation, migration, mock-service, and offline pipeline checks rather than a committed `pytest` suite.

## Production deployment

Before deployment:

1. Provision Supabase Cloud or a persistent self-hosted Supabase stack.
2. Create the private `pharmalens-docs` bucket and apply the Storage policies.
3. Store secrets in the deployment secret manager, not in an image or repository file.
4. Set production Supabase URLs and the correct PostgreSQL connection string.
5. Run `alembic upgrade head` against the production database.
6. Confirm the Supabase RLS linter no longer reports disabled RLS for application tables.
7. Restrict `CORS_ORIGINS` to the deployed frontend origin.
8. Put the API behind HTTPS and a reverse proxy or managed ingress.
9. Use a process manager with restart behavior and monitor `/api/health` and application logs.
10. Back up PostgreSQL and Storage volumes independently.
11. Rotate credentials that were exposed during development.

The current API does not implement application-level user authentication or authorization. Do not expose it as a public multi-user production API until an authentication and authorization layer is added. RLS protects direct database access, but it does not replace API authentication.

For a containerized backend, use the internal Supabase service hostname and port available on the deployment network. Do not copy the local host-mapped database address `127.0.0.1:54322` into a container environment unless PostgreSQL is actually exposed there.

## Troubleshooting

### `npx supabase start` fails

Run it from `D:\Resume\PharmaLens`, confirm Docker Desktop is running, and check that ports `54321`, `54322`, and `54323` are available.

### `alembic upgrade head` cannot connect

Confirm that the virtual environment is active and that `SUPABASE_DB_URL` points to the same Supabase project or local stack that is running. Local Supabase normally exposes PostgreSQL on port `54322`.

### The RLS linter still reports `rls_disabled_in_public`

Run `alembic current`, confirm `002_enable_public_rls` is the head, and verify that the migration was applied to the exact database scanned by Supabase. A migration applied to a different Cloud project will not change the linter result.

### Upload returns an error

Check the extension, MIME type, file signature, 300 MiB limit, bucket name, Storage URL, publishable key, and Storage policies. The service rejects files before analysis when they are empty, malformed, unsupported, or oversized.

### Analysis reaches `failed`

Inspect the backend logs for LLM, parser, Storage, or database details. Verify the configured provider key, template sections, document extraction output, and network access. The API intentionally returns a safe failure message instead of raw provider or database details.

### Dolphin parsing does not start

Confirm `requirements-dolphin.txt` is installed, `DOLPHIN_MODEL_PATH` points to usable weights, and the selected device is available. Use `DOCUMENT_PARSER_PROVIDER=native` while validating the rest of the backend.

## Related documentation

The project-level architecture, requirements, design, rules, and execution plan are in the repository root:

- [`PharmaLens_Architecture.md`](../PharmaLens_Architecture.md)
- [`PharmaLens_Backend_PRD.md`](../PharmaLens_Backend_PRD.md)
- [`PharmaLens_Rules.md`](../PharmaLens_Rules.md)
- [`PharmaLens_Phases.md`](../PharmaLens_Phases.md)
- [`memory.md`](../memory.md)
