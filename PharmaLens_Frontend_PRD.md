# Product Requirements Document — PharmaLens Frontend

## 1. Basic Information

| Field | Details |
|-------|---------|
| **Feature Name** | PharmaLens — AI-Powered Regulatory Compliance Copilot (Frontend) |
| **Owner** | Bhuvan Nagesh |
| **Developers** | Bhuvan N |
| **Contributors** | — |
| **Created Date** | 28-09-2026 |
| **Last Updated** | 28-09-2026 |
| **Status** | Planning |
| **Priority** | High |
| **Related Issue / Task** | PHARMALENS-FRONTEND-001 |

---

## 2. Problem Statement / Feature Explanation

### Problem

The PharmaLens backend provides REST APIs for document upload, compliance analysis triggering, and report retrieval. However, without a well-designed React frontend, users have no way to interact with the system. The frontend must provide:

1. An intuitive **document upload interface** that accepts PDF/DOCX files
2. A **compliance template selector** so users can choose which regulatory framework to analyze against
3. A **real-time analysis status indicator** showing pipeline progress
4. A **comprehensive gap report dashboard** displaying compliance gaps with severity indicators, descriptions, and corrective action recommendations
5. An **analysis history view** enabling users to review and compare past analyses

**Why are we building this?**
- To make PharmaLens a complete, usable product — not just a backend API
- To demonstrate React component architecture, state management, and responsive design skills
- To showcase SPA (Single Page Application) development with professional UI patterns

### Feature Explanation

The PharmaLens frontend is a **React Single Page Application** that consumes the FastAPI backend APIs. It has 4 primary views:

1. **Dashboard** — Overview of recent documents and analyses with quick-action cards
2. **Document Upload** — Drag-and-drop file upload with template selection and analysis trigger
3. **Analysis Report** — Detailed compliance gap report with severity badges, expandable gap cards, and corrective action lists
4. **Analysis History** — Table of all past analyses with filters and comparison capabilities

```
┌─────────────────────────────────────────────────────────────────┐
│                     PharmaLens React App                        │
│                                                                 │
│  ┌─────────┐  ┌──────────────┐  ┌───────────┐  ┌────────────┐ │
│  │Dashboard │  │ Upload &     │  │ Analysis  │  │  History   │ │
│  │ Overview │  │ Analyze      │  │  Report   │  │  & Compare │ │
│  └─────────┘  └──────────────┘  └───────────┘  └────────────┘ │
│                         │                                       │
│                    REST API calls                               │
│                         │                                       │
│              ┌──────────▼──────────┐                           │
│              │   FastAPI Backend   │                           │
│              └─────────────────────┘                           │
└─────────────────────────────────────────────────────────────────┘
```

---

## 3. Objective

### Goals

- **Goal 1:** Build a production-quality React SPA with component-based architecture
- **Goal 2:** Implement 4 core views: Dashboard, Upload & Analyze, Analysis Report, History
- **Goal 3:** Consume all backend REST APIs with proper loading, error, and empty states
- **Goal 4:** Design a responsive, modern UI that communicates compliance data clearly
- **Goal 5:** Implement client-side routing with React Router
- **Goal 6:** Use proper state management for API data (React hooks + context or zustand)

### Success Metrics

- All 4 views render correctly with real API data
- File upload works for PDF and DOCX files with proper validation feedback
- Analysis report displays all gaps with severity indicators and corrective actions
- UI is responsive across desktop and tablet viewports
- All error states from the backend are handled with user-friendly messages

---

## 4. User Flow

```
User opens PharmaLens at http://localhost:5173
  ↓
Dashboard loads → GET /api/documents + GET /api/analyses (recent)
  ↓
Dashboard shows: document count, analysis count, recent analyses cards
  ↓
User clicks "New Analysis" or navigates to Upload page
  ↓
Upload page renders:
  - Drag-and-drop file zone (accepts .pdf, .docx)
  - Template selector dropdown (populated via GET /api/templates)
  - "Analyze" button (disabled until file + template selected)
  ↓
User drops a PDF file → file preview shows (name, size, type)
  ↓
User selects "FDA SOP Compliance Template" from dropdown
  ↓
User clicks "Analyze"
  ↓
Step 1: POST /api/documents (file upload) → returns document_id
Step 2: POST /api/analyses { document_id, template_id } → returns analysis_id
  ↓
UI shows analysis progress indicator (polling GET /api/analyses/:id every 3s)
  ↓
Status: "processing" → spinner with "AI agents analyzing your document..."
  ↓
Status: "completed" → auto-redirect to Analysis Report page
  ↓
Analysis Report page:
  - Summary card: total gaps, critical/major/minor counts with color-coded badges
  - Expandable gap cards: each shows section name, severity badge, gap type, description
  - Nested corrective action list under each gap
  - "Download Report" button (optional, generates PDF/JSON)
  ↓
User clicks "History" in navigation
  ↓
History page: table of all analyses with columns:
  Document | Template | Status | Gaps | Date | Actions
  ↓
User clicks "View Report" on any row → navigates to that analysis report
```

---

## 5. Feature Impact

### Impacted Pages / Routes

| Route | Page | Purpose |
|-------|------|---------|
| `/` | Dashboard | Overview of documents and recent analyses |
| `/upload` | Upload & Analyze | File upload, template selection, analysis trigger |
| `/analysis/:id` | Analysis Report | Detailed gap report with corrective actions |
| `/history` | Analysis History | Table of all past analyses |

### Impacted Components

| Component | Purpose |
|-----------|---------|
| `App.jsx` | Root component with React Router setup |
| `Navbar.jsx` | Top navigation bar with links to all 4 pages |
| `Dashboard.jsx` | Overview page with stat cards and recent analyses |
| `StatCard.jsx` | Reusable card displaying a count + label (e.g., "3 Critical Gaps") |
| `UploadPage.jsx` | File upload zone + template selector + analyze button |
| `FileDropZone.jsx` | Drag-and-drop file upload area with validation |
| `TemplateSelector.jsx` | Dropdown populated from GET /api/templates |
| `AnalysisProgress.jsx` | Polling-based progress indicator during analysis |
| `AnalysisReport.jsx` | Full analysis report page |
| `GapSummaryCard.jsx` | Summary showing total/critical/major/minor gap counts |
| `GapCard.jsx` | Expandable card for a single gap (severity, description, actions) |
| `SeverityBadge.jsx` | Color-coded badge: Critical (red), Major (orange), Minor (yellow) |
| `CorrectiveActionList.jsx` | List of recommendations under a gap card |
| `HistoryPage.jsx` | Table of all analyses with filters |
| `AnalysisRow.jsx` | Single row in the history table |
| `EmptyState.jsx` | Reusable empty state illustration + message |
| `LoadingSpinner.jsx` | Reusable loading indicator |
| `ErrorBanner.jsx` | Reusable error message display |

### Consumed APIs

| API | Where Used |
|-----|-----------|
| `GET /api/documents` | Dashboard (document count) |
| `POST /api/documents` | UploadPage (file upload) |
| `GET /api/templates` | UploadPage (TemplateSelector dropdown) |
| `POST /api/analyses` | UploadPage (trigger analysis) |
| `GET /api/analyses/:id` | AnalysisReport + AnalysisProgress (polling) |
| `GET /api/analyses` | HistoryPage (list all), Dashboard (recent) |

### Backend Environment Contract

The frontend never connects directly to PostgreSQL or Supabase. It calls the FastAPI backend through `VITE_API_BASE_URL`. The backend connects to the self-hosted Supabase Docker stack, and this infrastructure choice does not change the frontend API contract.

```env
VITE_API_BASE_URL=http://localhost:8000
```

For a deployed frontend, set this value to the deployed FastAPI base URL and add the frontend origin to the backend `CORS_ORIGINS` setting.

---

## 6. Implementation Breakdown

### Frontend — React Application Structure

```
pharmalens-frontend/
├── public/
│   └── index.html
├── src/
│   ├── main.jsx                     # React entry point
│   ├── App.jsx                      # Router setup + layout
│   ├── App.css                      # Global styles
│   │
│   ├── components/
│   │   ├── layout/
│   │   │   ├── Navbar.jsx           # Top navigation bar
│   │   │   └── PageContainer.jsx    # Wrapper with padding + max-width
│   │   │
│   │   ├── common/
│   │   │   ├── StatCard.jsx         # Reusable stat display card
│   │   │   ├── SeverityBadge.jsx    # Critical/Major/Minor colored badge
│   │   │   ├── LoadingSpinner.jsx   # Spinner component
│   │   │   ├── EmptyState.jsx       # Empty state with illustration
│   │   │   └── ErrorBanner.jsx      # Error display banner
│   │   │
│   │   ├── upload/
│   │   │   ├── FileDropZone.jsx     # Drag-and-drop file input
│   │   │   ├── TemplateSelector.jsx # Template dropdown
│   │   │   └── AnalysisProgress.jsx # Progress polling indicator
│   │   │
│   │   ├── report/
│   │   │   ├── GapSummaryCard.jsx   # Gap count summary with badges
│   │   │   ├── GapCard.jsx          # Expandable gap detail card
│   │   │   └── CorrectiveActionList.jsx # Recommendation list
│   │   │
│   │   └── history/
│   │       └── AnalysisRow.jsx      # History table row
│   │
│   ├── pages/
│   │   ├── Dashboard.jsx            # Dashboard overview page
│   │   ├── UploadPage.jsx           # Upload + analyze page
│   │   ├── AnalysisReport.jsx       # Full report page
│   │   └── HistoryPage.jsx          # Analysis history page
│   │
│   ├── services/
│   │   └── api.js                   # Axios/fetch wrapper for all API calls
│   │
│   ├── hooks/
│   │   ├── useDocuments.js          # Custom hook for document operations
│   │   ├── useAnalyses.js           # Custom hook for analysis operations
│   │   └── useTemplates.js          # Custom hook for template operations
│   │
│   └── utils/
│       ├── constants.js             # API base URL, severity colors, etc.
│       └── formatters.js            # Date formatting, file size formatting
│
├── package.json
└── vite.config.js
```

### Frontend — Key Component Specifications

#### FileDropZone.jsx
- Accepts drag-and-drop + click-to-browse
- Validates file type on drop (only `.pdf`, `.docx`)
- Shows file preview: name, size (formatted), type icon
- Shows error state if invalid file type dropped
- Props: `onFileSelect(file)`, `acceptedTypes`, `maxSizeMB`

#### TemplateSelector.jsx
- Fetches templates from `GET /api/templates` on mount
- Renders a styled dropdown/select with template name + framework
- Loading state while fetching
- Empty state if no templates exist
- Props: `onTemplateSelect(templateId)`, `selectedTemplateId`

#### AnalysisProgress.jsx
- Receives `analysisId` as prop
- Polls `GET /api/analyses/:id` every 3 seconds
- Shows animated progress indicator with stage labels:
  - "Extracting document sections..."
  - "Mapping to regulatory framework..."
  - "Analyzing compliance gaps..."
  - "Generating corrective actions..."
- Calls `onComplete(analysisData)` when status = "completed"
- Calls `onError(error)` when status = "failed"

#### GapCard.jsx
- Expandable/collapsible card
- Header: section name + SeverityBadge + gap type tag
- Body (expanded): gap description + CorrectiveActionList
- Click header to toggle expand/collapse
- Props: `gap` (object with severity, description, corrective_actions)

#### SeverityBadge.jsx
- Color-coded pill badge
- Critical → red background (#DC2626)
- Major → orange background (#EA580C)
- Minor → yellow background (#CA8A04)
- Props: `severity` ("critical" | "major" | "minor")

### Frontend — State Management

Use **React hooks** (useState, useEffect) with **custom hooks** for API operations:

```javascript
// hooks/useAnalyses.js
function useAnalyses() {
  const [analyses, setAnalyses] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const fetchAnalyses = async (filters) => { /* GET /api/analyses */ };
  const getAnalysis = async (id) => { /* GET /api/analyses/:id */ };
  const triggerAnalysis = async (documentId, templateId) => { /* POST /api/analyses */ };

  return { analyses, loading, error, fetchAnalyses, getAnalysis, triggerAnalysis };
}
```

### Frontend — Routing

```jsx
<BrowserRouter>
  <Navbar />
  <Routes>
    <Route path="/" element={<Dashboard />} />
    <Route path="/upload" element={<UploadPage />} />
    <Route path="/analysis/:id" element={<AnalysisReport />} />
    <Route path="/history" element={<HistoryPage />} />
  </Routes>
</BrowserRouter>
```

### Frontend — Styling Approach

- **Vanilla CSS** with CSS custom properties (design tokens)
- Design tokens defined in `App.css`:
  ```css
  :root {
    --color-primary: #004F90;
    --color-critical: #DC2626;
    --color-major: #EA580C;
    --color-minor: #CA8A04;
    --color-success: #16A34A;
    --color-bg: #F8FAFC;
    --color-card: #FFFFFF;
    --color-text: #1E293B;
    --color-text-muted: #64748B;
    --color-border: #E2E8F0;
    --radius: 8px;
    --shadow-sm: 0 1px 2px rgba(0,0,0,0.05);
    --shadow-md: 0 4px 6px -1px rgba(0,0,0,0.1);
    --font-sans: 'Inter', system-ui, sans-serif;
  }
  ```
- Each component has a co-located `.css` file (e.g., `GapCard.css`)
- Responsive breakpoints: 768px (tablet), 1024px (desktop)

---

## 7. Functional Requirements

| ID | Requirement | Acceptance Criteria |
|----|-------------|---------------------|
| FR-1 | Dashboard shows document count and analysis count | Stat cards display correct numbers from API |
| FR-2 | Dashboard shows 5 most recent analyses | Recent analyses cards render with document name, template, status, date |
| FR-3 | File drop zone accepts PDF and DOCX files | Dropping a .pdf or .docx shows file preview; other types show error |
| FR-4 | File drop zone rejects unsupported file types | Error message displayed; "Analyze" button remains disabled |
| FR-5 | Template selector populates from API | Dropdown lists all templates with name and framework |
| FR-6 | "Analyze" button requires both file and template | Button disabled until both are selected; enabled when both present |
| FR-7 | Clicking "Analyze" uploads file then triggers analysis | Sequential API calls: POST /documents → POST /analyses |
| FR-8 | Analysis progress indicator polls until complete | Polls every 3s; shows animated stage messages; auto-navigates on completion |
| FR-9 | Analysis report shows gap summary | Summary card with total, critical, major, minor counts + colored badges |
| FR-10 | Analysis report shows expandable gap cards | Each gap card shows section name, severity, type, description |
| FR-11 | Gap cards contain corrective action recommendations | Expanding a gap card reveals its corrective action list |
| FR-12 | History page shows all analyses in a table | Columns: Document, Template, Status, Gaps, Date, Actions |
| FR-13 | "View Report" in history navigates to report page | Clicking navigates to /analysis/:id |
| FR-14 | All pages handle loading states | LoadingSpinner shown while API calls are pending |
| FR-15 | All pages handle error states | ErrorBanner shown with user-friendly message on API failure |
| FR-16 | All pages handle empty states | EmptyState component shown when no data exists |
| FR-17 | Navigation bar highlights active page | Current page link is visually active |
| FR-18 | UI is responsive on desktop (1024px+) and tablet (768px+) | Layout adjusts; cards stack vertically on smaller screens |

---

## 8. UI Wireframes (Text-Based)

### Dashboard

```
┌─────────────────────────────────────────────────────────────┐
│  🔬 PharmaLens          Dashboard │ Upload │ History        │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────┐ │
│  │  📄 12      │  │  🔍 8       │  │  ⚠️ 3 Critical     │ │
│  │  Documents  │  │  Analyses   │  │  Gaps (Latest)      │ │
│  └─────────────┘  └─────────────┘  └─────────────────────┘ │
│                                                             │
│  Recent Analyses                          [New Analysis →]  │
│  ┌─────────────────────────────────────────────────────────┐│
│  │ SOP-Manufacturing-v3.pdf │ FDA SOP │ 3 gaps │ 28 Sep   ││
│  │ BMR-Batch-42.pdf         │ ICH Q10 │ 5 gaps │ 27 Sep   ││
│  │ Deviation-Report-19.docx │ FDA SOP │ 1 gap  │ 26 Sep   ││
│  └─────────────────────────────────────────────────────────┘│
└─────────────────────────────────────────────────────────────┘
```

### Upload & Analyze

```
┌─────────────────────────────────────────────────────────────┐
│  🔬 PharmaLens          Dashboard │ Upload │ History        │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  Upload & Analyze                                           │
│                                                             │
│  ┌─────────────────────────────────────────────────────────┐│
│  │                                                         ││
│  │        📁 Drag & drop your PDF or DOCX file here       ││
│  │              or click to browse files                   ││
│  │                                                         ││
│  │        ✅ SOP-Manufacturing-v3.pdf (2.4 MB)            ││
│  │                                                         ││
│  └─────────────────────────────────────────────────────────┘│
│                                                             │
│  Compliance Template:                                       │
│  ┌─────────────────────────────────────────────────────┐   │
│  │ FDA SOP Compliance Template (21 CFR Part 211)  ▼    │   │
│  └─────────────────────────────────────────────────────┘   │
│                                                             │
│                              [ 🔍 Analyze Document ]        │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### Analysis Report

```
┌─────────────────────────────────────────────────────────────┐
│  🔬 PharmaLens          Dashboard │ Upload │ History        │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  Analysis Report — SOP-Manufacturing-v3.pdf                 │
│  Template: FDA SOP Compliance Template                      │
│  Analyzed: 28 Sep 2026, 7:31 PM                             │
│                                                             │
│  ┌────────┐  ┌────────┐  ┌────────┐  ┌────────┐           │
│  │ 3 Total│  │ 1 Crit │  │ 1 Major│  │ 1 Minor│           │
│  │  Gaps  │  │  🔴    │  │  🟠    │  │  🟡    │           │
│  └────────┘  └────────┘  └────────┘  └────────┘           │
│                                                             │
│  ┌─────────────────────────────────────────────────────┐   │
│  │ 🔴 CRITICAL │ Safety Precautions          │ Missing │   │
│  ├─────────────────────────────────────────────────────┤   │
│  │ The document does not contain a dedicated Safety    │   │
│  │ Precautions section. FDA 21 CFR Part 211 requires   │   │
│  │ documented safety procedures for manufacturing.     │   │
│  │                                                     │   │
│  │ 💡 Corrective Action:                               │   │
│  │ • Add a Safety Precautions section covering:        │   │
│  │   required PPE, chemical handling procedures,       │   │
│  │   emergency response protocols...          [HIGH]   │   │
│  └─────────────────────────────────────────────────────┘   │
│                                                             │
│  ┌─────────────────────────────────────────────────────┐   │
│  │ 🟠 MAJOR │ Revision History          │ Incomplete   │   │
│  │  ► Click to expand                                  │   │
│  └─────────────────────────────────────────────────────┘   │
│                                                             │
│  ┌─────────────────────────────────────────────────────┐   │
│  │ 🟡 MINOR │ References                │ Incomplete   │   │
│  │  ► Click to expand                                  │   │
│  └─────────────────────────────────────────────────────┘   │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

## 9. Edge Cases

### UI Edge Cases

- User drops multiple files → only accept the first file; ignore others
- User drops a file then drops another → replace the first file preview
- Template list is empty (no templates created yet) → show message "No compliance templates available. Please create one first."
- Analysis takes longer than 60 seconds → show "This is taking longer than expected. Please wait..." message
- Analysis fails → show error banner with "Analysis failed. Please try again with a different document." + retry button
- User navigates away during analysis → polling stops (cleanup on unmount)
- User directly navigates to `/analysis/invalid-uuid` → 404 from API → show "Analysis not found" page
- Browser back button from report → returns to previous page (history or upload)
- Very long gap descriptions → text truncated with "Read more" toggle
- Many gaps (20+) → virtualized list or paginated gap cards

### Responsive Edge Cases

- Stat cards on mobile → stack vertically (1 column)
- History table on mobile → horizontal scroll or card layout
- File drop zone on mobile → click-to-browse only (no drag-and-drop)
- Long filenames → truncated with ellipsis + tooltip on hover

### Network Edge Cases

- API server unreachable → error banner "Unable to connect to the server. Please check your connection."
- Slow network → loading spinners prevent premature interaction
- API returns 500 → generic error banner with retry option

---

## 10. Test Cases

| Test ID | Scenario | Steps | Expected Result |
|---------|----------|-------|-----------------|
| TC-001 | Dashboard loads | Navigate to / | Stat cards + recent analyses render |
| TC-002 | Empty dashboard | No documents/analyses exist | EmptyState shown |
| TC-003 | Upload PDF | Drop a .pdf file on FileDropZone | File preview shown (name, size) |
| TC-004 | Upload DOCX | Drop a .docx file on FileDropZone | File preview shown (name, size) |
| TC-005 | Reject unsupported file | Drop a .txt file | Error message shown |
| TC-006 | Select template | Open TemplateSelector dropdown | All templates listed |
| TC-007 | Analyze button state | No file selected | Button disabled |
| TC-008 | Analyze button state | File + template selected | Button enabled |
| TC-009 | Trigger analysis | Click Analyze with valid inputs | Upload → trigger → progress indicator shown |
| TC-010 | Analysis progress | Wait for completion | Auto-navigate to report page |
| TC-011 | Report summary | View analysis report | Correct gap counts with severity badges |
| TC-012 | Expand gap card | Click a collapsed gap card | Description + corrective actions visible |
| TC-013 | Collapse gap card | Click an expanded gap card | Card collapses |
| TC-014 | History table | Navigate to /history | All analyses listed in table |
| TC-015 | View report from history | Click "View Report" on a row | Navigates to /analysis/:id |
| TC-016 | Loading state | Slow API response | LoadingSpinner visible |
| TC-017 | Error state | API returns 500 | ErrorBanner with friendly message |
| TC-018 | Responsive layout | Resize to 768px | Layout adapts (cards stack) |

---

## 11. Development & Testing Checklist

### Development

- [ ] React project setup with Vite + React Router
- [ ] Global CSS with design tokens (colors, spacing, typography)
- [ ] Navbar component with active-page highlighting
- [ ] Dashboard page with stat cards and recent analyses
- [ ] FileDropZone with drag-and-drop + click-to-browse + file type validation
- [ ] TemplateSelector dropdown with API integration
- [ ] UploadPage with sequential upload → analyze flow
- [ ] AnalysisProgress with 3-second polling and animated stage messages
- [ ] AnalysisReport page with GapSummaryCard + expandable GapCards
- [ ] SeverityBadge and CorrectiveActionList components
- [ ] HistoryPage with analysis table
- [ ] EmptyState, LoadingSpinner, ErrorBanner reusable components
- [ ] Custom hooks (useDocuments, useAnalyses, useTemplates) for API operations
- [ ] API service layer (services/api.js) with base URL configuration
- [ ] Responsive CSS for desktop + tablet

### Testing

- [ ] All 4 pages render correctly with mock/real API data
- [ ] File upload accepts PDF/DOCX and rejects other types
- [ ] Analysis flow works end-to-end (upload → trigger → poll → report)
- [ ] All loading, error, and empty states display correctly
- [ ] Navigation works across all pages
- [ ] Responsive layout verified at 768px and 1024px

### Final Verification

- [ ] No console errors in browser dev tools
- [ ] All API calls use correct endpoints and handle all response codes
- [ ] UI matches wireframes
- [ ] Component cleanup (unmount polling, cancel pending requests)

---

## 12. Acceptance Criteria

- [ ] Dashboard shows correct document count, analysis count, and recent analyses
- [ ] File upload accepts only PDF and DOCX with visual feedback
- [ ] Template selector shows all templates from the API
- [ ] Analyze button is disabled until both file and template are selected
- [ ] Analysis progress indicator polls and shows animated stage messages
- [ ] Report page displays gap summary with critical/major/minor counts
- [ ] Gap cards are expandable with severity badges, descriptions, and corrective actions
- [ ] History page lists all analyses in a sortable table
- [ ] All loading, error, and empty states are handled gracefully
- [ ] UI is responsive at desktop and tablet breakpoints

---

## 13. Risks & Dependencies

### Risks

| Risk | Mitigation |
|------|-----------|
| Backend APIs not ready when frontend development starts | Use mock data / MSW (Mock Service Worker) for development |
| Analysis polling may create unnecessary API load | Poll every 3s with auto-stop after 120s (timeout) |
| Large analysis reports with many gaps | Implement expandable cards; consider pagination for 20+ gaps |

### Technical Dependencies

- PharmaLens Backend (FastAPI) running and accessible
- Node.js 18+ for Vite build tooling
- React 18+, React Router v6+

---

## 14. Estimated Timeline

| Task | Estimate |
|------|----------|
| React project setup (Vite, Router, global CSS, design tokens) | 0.5 days |
| Reusable components (Navbar, StatCard, SeverityBadge, LoadingSpinner, ErrorBanner, EmptyState) | 1 day |
| Dashboard page | 0.5 days |
| Upload page (FileDropZone + TemplateSelector + AnalysisProgress) | 1.5 days |
| Analysis Report page (GapSummaryCard + GapCard + CorrectiveActionList) | 1.5 days |
| History page | 0.5 days |
| API service layer + custom hooks | 0.5 days |
| Responsive CSS + polish | 0.5 days |
| Testing + debugging | 0.5 days |
| **Total** | **7 days** |

---
