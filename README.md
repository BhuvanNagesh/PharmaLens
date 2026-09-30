# PharmaLens

PharmaLens is a pharmaceutical compliance document analysis platform. It accepts regulatory PDF and DOCX documents, stores the originals in private Supabase Storage, extracts their text, maps content to compliance-template sections, identifies gaps, proposes corrective actions, and produces a deterministic compliance score.

## Project status

- Backend implementation through Phase 3 is complete.
- The backend includes document processing, Supabase Storage integration, template management, asynchronous LangGraph analysis, persistence, audit logging, failure recovery, and database RLS hardening.
- Migration `002_enable_public_rls` is implemented and must be applied to the same database inspected by the Supabase linter.
- Frontend implementation is scheduled for Phase 4 and is not yet included in this repository.

For day-to-day backend installation, API usage, analysis polling, verification, and deployment instructions, see the [backend operator guide](pharmalens-backend/README.md).

## Architecture

```text
Browser / future frontend
          |
          v
FastAPI backend
  |       |       |
  |       |       +--> Google Gemini or OpenAI-compatible LLM provider
  |       |
  |       +----------> Supabase Storage: private pharmalens-docs bucket
  |
  +------------------> Supabase PostgreSQL database
                         |
                         +--> local Docker Supabase stack during development
                         +--> managed or self-hosted Supabase deployment
```

The application uses one Supabase architecture for both local development and deployment. Local Supabase runs through Docker and provides PostgreSQL, Storage, the API gateway, and Studio. The backend connects through `SUPABASE_URL` and `SUPABASE_DB_URL`; it does not use a separate MongoDB or standalone PostgreSQL installation.

## Implemented capabilities

- PDF and DOCX upload with a 300 MiB per-file limit.
- File signature and MIME validation before persistence.
- Native PDF/DOCX text extraction, including DOCX table content.
- Optional Dolphin-v2 document parsing integration for richer layout-aware extraction.
- Private Supabase Storage bucket named `pharmalens-docs`.
- Compliance-template and template-section CRUD APIs.
- Four-stage LangGraph workflow:
  1. document parser,
  2. compliance mapper,
  3. gap analyzer,
  4. corrective-action generator.
- Deterministic score calculation and severity classification.
- Background analysis execution with persisted `queued`, `processing`, `completed`, and `failed` states.
- Startup recovery for analyses interrupted by a process restart.
- Audit-log persistence for important backend operations.
- RLS enabled on application tables with no public `anon` or `authenticated` table policies by default.
- Generic public error responses while detailed failures remain in server logs.

## Repository layout

```text
PharmaLens/
├── pharmalens-backend/
│   ├── app/
│   │   ├── agents/              # LangGraph nodes and LLM configuration
│   │   ├── api/                 # FastAPI route handlers
│   │   ├── core/                # Settings, database, logging, and dependencies
│   │   ├── models/              # SQLAlchemy models
│   │   ├── schemas/             # Pydantic request and response schemas
│   │   ├── services/            # Storage, extraction, and analysis services
│   │   └── utils/               # Seed and support utilities
│   ├── alembic/
│   │   └── versions/
│   │       ├── 001_initial_schema.py
│   │       └── 002_enable_public_rls.py
│   ├── main.py
│   ├── requirements.txt
│   ├── requirements-dolphin.txt
│   └── .env                     # Local secrets; ignored by Git
├── pharmalens-frontend/         # Reserved for Phase 4 implementation
├── supabase/
│   ├── config.toml
│   └── migrations/20260930000000_storage_policies.sql
├── PharmaLens_Architecture.md
├── PharmaLens_Backend_PRD.md
├── PharmaLens_Design.md
├── PharmaLens_Frontend_PRD.md
├── PharmaLens_Phases.md
├── PharmaLens_Rules.md
├── memory.md
└── README.md
```

## Prerequisites

- Windows, macOS, or Linux.
- Python 3.11 or newer.
- Docker Desktop with at least 4 GB of memory allocated to Docker for the local Supabase stack.
- Node.js and `npx` for the Supabase CLI workflow.
- A Google API key, or an OpenAI API key when using the fallback provider.
- Optional: Dolphin-v2 model runtime and model weights for layout-aware document parsing.

## Start the local Supabase stack

Run these commands from the repository root, the directory that contains `supabase/config.toml`:

```powershell
cd D:\Resume\PharmaLens
npx supabase start
npx supabase status
```

`supabase status` prints the local API URL, database URL, publishable key, and Studio URL. Copy the values needed by the backend into `pharmalens-backend\.env`; do not copy secrets into this README or commit them to Git.

Typical local endpoints are:

```text
Supabase API:    http://127.0.0.1:54321
PostgreSQL:      127.0.0.1:54322
Supabase Studio: http://127.0.0.1:54323
```

The local Storage files are held by Docker volumes. Their capacity is limited by available disk space rather than the Supabase Cloud free-tier quota. Keep those volumes backed up if the data matters.

## Install and configure the backend

```powershell
cd D:\Resume\PharmaLens\pharmalens-backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
```

The default parser is the built-in native parser, so Dolphin is not required for the standard setup. To install the optional Dolphin dependencies:

```powershell
pip install -r requirements-dolphin.txt
```

Dolphin model weights are not included in the repository. Configure a valid local model path only after the optional runtime and weights are available.

Create `pharmalens-backend\.env` with values appropriate for the environment. This is a safe shape for local Docker development; replace the marked secret values locally:

```dotenv
SUPABASE_URL=http://127.0.0.1:54321
SUPABASE_PUBLISHABLE_KEY=<publishable-key-from-supabase-status>
SUPABASE_DB_URL=postgresql+asyncpg://postgres:postgres@127.0.0.1:54322/postgres
STORAGE_BUCKET=pharmalens-docs
STORAGE_TIMEOUT_SECONDS=120

GOOGLE_API_KEY=<google-api-key>
OPENAI_API_KEY=<optional-openai-api-key>
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

For Supabase Cloud, use the Cloud project URL, publishable key, and pooled or direct PostgreSQL connection string supplied by that project instead of the local values. Keep the variable names the same so application code does not change between environments.

Never commit `.env` files, publishable keys, database passwords, or LLM keys. Any credential previously pasted into a chat, issue, screenshot, or repository should be rotated before deployment.

## Apply the database schema and security migration

With the backend virtual environment active and `SUPABASE_DB_URL` pointing at the intended database:

```powershell
cd D:\Resume\PharmaLens\pharmalens-backend
alembic upgrade head
python -m app.utils.seed_templates
```

The migrations create the application tables and then enable RLS on:

```text
alembic_version
compliance_templates
template_sections
documents
analyses
analysis_gaps
corrective_actions
audit_logs
```

The RLS migration intentionally creates no broad public table policies. The trusted FastAPI database connection is the application access path. If the Supabase database linter still reports `rls_disabled_in_public`, verify that `SUPABASE_DB_URL` points to the same database being inspected and run `alembic upgrade head` again.

The storage policy migration is located at `supabase/migrations/20260930000000_storage_policies.sql`. Apply it through the Supabase migration workflow used for the target environment, then verify that the `pharmalens-docs` bucket exists and remains private.

## Run the backend

```powershell
cd D:\Resume\PharmaLens\pharmalens-backend
.\.venv\Scripts\Activate.ps1
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

Useful URLs:

```text
Health check: http://127.0.0.1:8000/api/health
OpenAPI UI:   http://127.0.0.1:8000/docs
ReDoc:        http://127.0.0.1:8000/redoc
```

## API surface

All routes are prefixed with `/api`.

| Method | Route | Purpose |
| --- | --- | --- |
| GET | `/api/health` | Service and dependency health response |
| POST | `/api/documents` | Upload and process a PDF or DOCX; returns `201` |
| GET | `/api/documents` | Paginated document collection |
| GET | `/api/documents/{document_id}` | Retrieve one document |
| DELETE | `/api/documents/{document_id}` | Delete document metadata and stored file; returns `204` |
| POST | `/api/templates` | Create a compliance template; returns `201` |
| GET | `/api/templates` | List compliance templates |
| GET | `/api/templates/{template_id}` | Retrieve one template with sections |
| PUT | `/api/templates/{template_id}` | Replace template data and sections |
| DELETE | `/api/templates/{template_id}` | Delete a template; returns `204` |
| POST | `/api/analyses` | Queue an analysis; returns `202` |
| GET | `/api/analyses` | List analyses with document and status filters |
| GET | `/api/analyses/{analysis_id}` | Retrieve analysis status or completed report |

The analysis request is asynchronous. After `POST /api/analyses`, poll `GET /api/analyses/{analysis_id}` until the status is `completed` or `failed`. A failed analysis stores a safe public failure message and retains diagnostic details in server logs.

## Analysis workflow

```text
Upload file
    |
    v
Validate signature and MIME type
    |
    v
Store original in private Supabase Storage
    |
    v
Extract native or Dolphin text
    |
    v
Parser -> compliance mapper -> gap analyzer -> corrective-action generator
    |
    v
Calculate deterministic score and persist the report
```

The current score is calculated from persisted gap severities:

```text
score = max(0, 100 - (critical_gaps * 25) - (major_gaps * 10) - (minor_gaps * 3))
```

The LLM proposes structured findings, but the final score is computed by backend code. The pipeline validates that every reported gap maps to a real template section and contains at least one corrective action before the result can be marked complete.

## Storage and security model

- The `pharmalens-docs` bucket is private.
- Uploads are limited to 300 MiB and supported PDF/DOCX content types.
- The backend uses the Supabase publishable key for Storage requests; a service-role key is not required by the current implementation and must not be exposed to a browser.
- Application tables have RLS enabled.
- No anonymous or authenticated public table policies are created by the RLS migration.
- CORS should be restricted to the deployed frontend origin before production.
- Production traffic should use HTTPS behind a reverse proxy or managed ingress.
- Database and Docker Storage volumes require an independent backup strategy.

## Verification commands

Run these checks from `pharmalens-backend` after installing dependencies:

```powershell
python -m compileall -q app main.py alembic
alembic history
```

The expected migration history ends at `002_enable_public_rls (head)`. The live Supabase database must also be checked by running `alembic upgrade head` and reviewing the Supabase database linter.

## Deployment checklist

1. Provision the target Supabase project or a persistent self-hosted Supabase stack.
2. Create the private `pharmalens-docs` bucket and apply the storage policies.
3. Set production `SUPABASE_URL`, `SUPABASE_PUBLISHABLE_KEY`, `SUPABASE_DB_URL`, and LLM credentials through the deployment secret manager.
4. Run `alembic upgrade head` against the target database.
5. Run the template seed utility only when the target environment needs the bundled seed templates.
6. Confirm the RLS linter is clean for application tables.
7. Set `CORS_ORIGINS` to the real frontend origin and place the API behind HTTPS.
8. Configure persistent backups for PostgreSQL and Storage.
9. Start the backend with a process manager and monitor `/api/health` and application logs.
10. Rotate every credential that was exposed during development or testing.

For a containerized backend deployment, use the internal Supabase service hostname and port supplied by the target stack rather than the local host-mapped port `54322`. The exact hostname depends on the deployment topology; do not copy local Docker URLs into production blindly.

## Troubleshooting

### Supabase will not start

Confirm Docker Desktop is running, execute `npx supabase status` from `D:\Resume\PharmaLens`, and check that the required local ports are available.

### The backend cannot connect to PostgreSQL

Check that `SUPABASE_DB_URL` matches the environment currently running. Local development normally uses port `54322`; a hosted or container-network connection normally uses a different hostname and port.

### The RLS linter still reports disabled RLS

Run `alembic current`, confirm the migration head is `002_enable_public_rls`, and ensure the connection string is for the same project and database scanned by the linter.

### An upload is rejected

Check the file extension, MIME type, file signature, size limit, bucket name, and Storage policy. The backend rejects empty, malformed, unsupported, or oversized files before analysis begins.

### An analysis fails

Inspect backend logs for the provider or extraction failure, verify the configured LLM key and provider, and query the analysis record for its safe failure status. The service retries transient LLM failures according to `LLM_MAX_ATTEMPTS` and does not expose raw provider errors in the API response.

### Dolphin parsing is unavailable

Use `DOCUMENT_PARSER_PROVIDER=native` for the supported built-in parser, or install `requirements-dolphin.txt`, provide valid model weights, and set `DOLPHIN_MODEL_PATH` before selecting Dolphin parsing.

## Project documentation

- [Architecture](PharmaLens_Architecture.md)
- [Backend product requirements](PharmaLens_Backend_PRD.md)
- [Frontend product requirements](PharmaLens_Frontend_PRD.md)
- [Design system](PharmaLens_Design.md)
- [Execution phases](PharmaLens_Phases.md)
- [Engineering and security rules](PharmaLens_Rules.md)
- [Current implementation memory](memory.md)
