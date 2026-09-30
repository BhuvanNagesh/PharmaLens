# PharmaLens — Design System Specification

> **Project:** PharmaLens — AI-Powered Regulatory Compliance Copilot  
> **Author:** Bhuvan Nagesh  
> **Created:** 29-09-2026  
> **Design Philosophy:** Clinical editorial intelligence meets regulatory authority  
> **Theme Strategy:** Light-first  
> **Status:** Pre-Implementation Design Spec  

---

## 0. Design Philosophy

PharmaLens is a **light-first, document-centric regulatory audit platform**. Its interface communicates calmness, scholarly precision, and institutional trustworthiness.

### Core Design Principles

1. **The Document is the Hero.**  
   PharmaLens exists to help users read, compare, annotate, and understand long regulatory documents (SOPs, batch records, validation protocols). The document reading surface must dominate the interface — every other UI element (navigation, controls, panels) exists in service of the document.

2. **Calm Authority, Not Urgent Alarm.**  
   Unlike DeviationFlow's kinetic mission-control energy, PharmaLens communicates **steady, focused analysis**. The interface should feel like a private regulatory reading room — quiet, organized, and deeply trustworthy. Motion is minimal. Alerts are restrained. Visual noise is eliminated.

3. **Brand at the Edges, Discipline at the Core.**  
   Maragsa is a visually striking editorial serif. It creates a memorable scholarly brand identity at controlled touchpoints — hero headings, report covers, empty states, and marketing moments. The operational core (document viewer, finding cards, compliance tables, audit panels) uses Lato and Arimo for maximum sustained readability.

4. **Regulatory Red as Signal, Not Saturation.**  
   The deep burgundy/crimson palette (`#C7372C`, `#710D0B`) is PharmaLens's brand signature. However, red carries inherent semantic weight in regulatory software (critical finding, non-compliance, failure). The red palette must therefore be applied with surgical precision — as a brand accent in safe contexts (headings, borders, icons) and as a severity indicator in compliance contexts — never as large saturated fills that create visual panic.

5. **Readability Above All.**  
   During multi-hour regulatory document reviews, eye fatigue is the primary usability threat. Typography, line spacing, contrast ratios, and surface colors are all calibrated for sustained comfortable reading — not for visual impact in a 3-second screenshot.

---

## 1. Typography System

PharmaLens uses a **two-layer typography architecture** that separates editorial brand identity from functional interface and document content.

### 1.1 Brand Typography Layer

Brand fonts appear at controlled editorial moments only. They are **never used** for document content, tables, forms, navigation, finding cards, audit records, or dense operational UI.

#### Primary Display — Maragsa

| Property | Value |
|----------|-------|
| **Font Family** | `'Maragsa', serif` |
| **Character** | High-contrast editorial serif with scholarly authority. Evokes peer-reviewed journal mastheads, university press identities, and authoritative institutional publications. |
| **Permitted Contexts** | Product wordmark, marketing hero headline, large editorial heading, formal report cover title, major empty-state statement, onboarding hero |
| **Forbidden Contexts** | Navigation, cards, tables, form labels, buttons, metadata, tooltips, finding descriptions, document body text, audit logs |
| **Loading Strategy** | `font-display: swap`, lazy-loaded. Not required for initial application render. |

#### Supporting Display — Arimo (Display Weight)

| Property | Value |
|----------|-------|
| **Font Family** | `'Arimo', sans-serif` (SemiBold 600 or Bold 700 at display sizes) |
| **Character** | Clean, functional counterweight to Maragsa's editorial drama. Grounds the brand in professionalism. |
| **Permitted Contexts** | Hero supporting text, product description beneath Maragsa heading, editorial captions, supporting headings in marketing pages |

#### Brand Typography Usage Examples

```
┌──────────────────────────────────────────────────────────────┐
│                                                              │
│   REGULATORY CLARITY.                 ← Maragsa 64px        │
│                                                              │
│   AI-powered compliance auditing for  ← Arimo 20px 600      │
│   pharmaceutical regulatory documents                        │
│                                                              │
└──────────────────────────────────────────────────────────────┘
```

```
┌──────────────────────────────────────────────────────────────┐
│                                                              │
│           NO DOCUMENTS UPLOADED YET.  ← Maragsa 40px        │
│                                                              │
│           Upload your first SOP or     ← Arimo 16px 400     │
│           batch record to begin                               │
│           compliance analysis.                                │
│                                                              │
│               [ Upload Document ]     ← Lato 14px 700       │
│                                                              │
└──────────────────────────────────────────────────────────────┘
```

#### Report Cover Page Typography

```
┌──────────────────────────────────────────────────────────────┐
│                                                              │
│                                                              │
│        COMPLIANCE AUDIT REPORT        ← Maragsa 48px        │
│                                                              │
│        SOP-QC-401 Revision 3          ← Arimo 18px 600      │
│        Quality Control Laboratory                             │
│        Procedures                                             │
│                                                              │
│        ──────────────────────                                 │
│                                                              │
│        Prepared by: Bhuvan Nagesh     ← Lato 13px 400       │
│        Date: 29 September 2026                                │
│        Template: FDA cGMP Compliance                          │
│                                                              │
│        Overall Compliance: 94%         ← Lato 14px 700      │
│        Critical Findings: 2                                   │
│                                                              │
└──────────────────────────────────────────────────────────────┘
```

---

### 1.2 Interface Typography Layer

Interface fonts handle 95%+ of the application surface. PharmaLens deliberately separates **application chrome** (Lato) from **document content** (Arimo) to create a clear visual distinction between the tool and the material being inspected.

#### Primary UI Font — Lato

| Property | Value |
|----------|-------|
| **Font Family** | `'Lato', sans-serif` |
| **Weights Used** | Regular 400, Bold 700 |
| **Character** | Warm humanist sans-serif with excellent clarity at small sizes. Professional without being cold. Ideal for application chrome, controls, and labels. |
| **Usage** | Navigation items, page titles (H1–H3), section headers, button labels, form labels, finding card headers, compliance score labels, modal titles, sidebar section labels, tab labels, filter controls |

#### Document Body / Data Font — Arimo

| Property | Value |
|----------|-------|
| **Font Family** | `'Arimo', sans-serif` |
| **Weights Used** | Regular 400, Medium 500, SemiBold 600 |
| **Feature Settings** | `font-variant-numeric: tabular-nums;` for compliance scores and percentages |
| **Character** | Metrically compatible with Arial. Exceptionally legible for sustained reading. Neutral — disappears so the regulatory content speaks. |
| **Usage** | Uploaded document extracted text, regulatory excerpts, audit finding descriptions, corrective action recommendations, long-form explanations, CFR clause references, template section content, compliance report body text, metadata values, timestamps |

#### Why Two Interface Fonts?

PharmaLens displays two distinct categories of text:

1. **Application text** — labels, headings, navigation, controls, and buttons that are part of the *tool*.
2. **Document text** — extracted PDF/DOCX content, regulatory clauses, and AI-generated analysis that is part of the *material being inspected*.

Using Lato for application chrome and Arimo for document content creates an **immediate visual boundary** between "the tool" and "the content." Users can instantly distinguish what is interface versus what is source material without needing borders or background colors.

---

### 1.3 Type Scale — Application Interface

| Token Name | Element | Font Family | Size | Line Height | Weight | Letter Spacing | Casing | Light Mode Color | Dark Mode Color |
|------------|---------|-------------|------|-------------|--------|----------------|--------|------------------|-----------------|
| `--type-display-hero` | Marketing Hero | Maragsa | 58–78px | 1.05 | Regular | `-0.02em` | Title Case | `#191211` | `#F5F3EF` |
| `--type-display-report` | Report Cover | Maragsa | 40–52px | 1.1 | Regular | `-0.01em` | UPPERCASE | `#191211` | `#F5F3EF` |
| `--type-display-sub` | Hero Support | Arimo | 18–22px | 1.5 | SemiBold 600 | `0em` | Sentence Case | `#4A4743` | `#C5C2BD` |
| `--type-h1` | Workspace Title | Lato | 28px | 36px | Bold 700 | `-0.02em` | Title Case | `#191211` | `#F5F3EF` |
| `--type-h2` | Section Title | Lato | 22px | 28px | Bold 700 | `-0.01em` | Title Case | `#191211` | `#F5F3EF` |
| `--type-h3` | Finding / Card | Lato | 17px | 22px | Bold 700 | `0em` | Sentence Case | `#191211` | `#F5F3EF` |
| `--type-h4` | Subsection | Lato | 14px | 18px | Bold 700 | `0em` | Sentence Case | `#191211` | `#F5F3EF` |
| `--type-body-ui` | Application Body | Lato | 14px | 20px | Regular 400 | `0em` | Sentence Case | `#4A4743` | `#C5C2BD` |
| `--type-body-doc` | Document Text | Arimo | 15px | 24px | Regular 400 | `0em` | Sentence Case | `#191211` | `#F5F3EF` |
| `--type-body-doc-sm` | Compact Doc Text | Arimo | 14px | 22px | Regular 400 | `0em` | Sentence Case | `#191211` | `#F5F3EF` |
| `--type-ui-label` | Control Labels | Lato | 13px | 16px | Bold 700 | `+0.01em` | Sentence Case | `#191211` | `#F5F3EF` |
| `--type-ui-small` | Small Labels | Lato | 12px | 14px | Bold 700 | `+0.03em` | UPPERCASE | `#94938F` | `#94938F` |
| `--type-metadata` | Secondary Info | Lato | 13px | 16px | Regular 400 | `0em` | Sentence Case | `#94938F` | `#94938F` |
| `--type-regulatory-ref` | CFR / Clause Ref | Arimo | 12px | 16px | SemiBold 600 | `+0.02em` | UPPERCASE / Mixed | `#710D0B` | `#E05247` |
| `--type-caption` | Captions / Help | Lato | 11px | 14px | Regular 400 | `+0.01em` | Sentence Case | `#94938F` | `#94938F` |

### 1.4 Document Reading Typography — Detailed Specification

The document reader is the most critical surface in PharmaLens. Its typography is calibrated for multi-hour sustained reading.

| Property | Value | Rationale |
|----------|-------|-----------|
| **Font** | Arimo, 15px | Slightly larger than UI body for comfortable extended reading |
| **Line Height** | `1.6` (24px) | Generous leading prevents line-skipping fatigue during long clauses |
| **Paragraph Spacing** | `16px` (margin-bottom) | Clear paragraph delineation in dense regulatory text |
| **Max Line Length** | `72ch` (characters) | Prevents extremely long lines that cause tracking fatigue |
| **Text Color** | `#191211` on `#FFFFFF` surface | Maximum contrast (18.2:1) without the harshness of pure `#000000` |
| **Highlight Color** | `#C7372C15` (red at 8%) underline + left margin marker | Subtle, non-destructive annotation |
| **Selected Text** | `#710D0B20` background | Brand-consistent selection highlight |

### 1.5 Typography Rules

1. **Sentence case** is the default for all interface and document text.
2. **UPPERCASE** is reserved exclusively for:
   - Severity tags (`CRITICAL`, `MAJOR`, `MINOR`, `COMPLIANT`)
   - Small metadata category labels (`SECTION`, `CLAUSE`, `SEVERITY`)
   - Regulatory reference codes (`FDA 21 CFR § 211.100(A)`)
   - Navigation category labels (when very short, e.g., `DOCUMENTS`, `TEMPLATES`)
3. **Never use all-caps for:**
   - Finding descriptions or corrective action text
   - Document body content
   - Audit log entries
   - Multi-word button labels exceeding 3 words
4. **Maragsa must never appear in:**
   - Any text smaller than 28px
   - Any context with more than ~8 words per line
   - Any repeating component (cards, list items, table rows)
   - Any form input or control label
5. **Tabular figures** must be enabled for all compliance percentages, scores, and numerical data displays.

---

## 2. Color System

### 2.1 Design Token Architecture

PharmaLens uses semantic color tokens mapped to primitive values, identical in architecture to DeviationFlow but with a completely different palette.

```
Primitive Palette (hex values)
        ↓
Semantic Tokens (role-based names)
        ↓
Component Tokens (component-specific overrides)
```

### 2.2 Primitive Color Palette

| Primitive Name | HEX | RGB | Character |
|----------------|-----|-----|-----------|
| `charcoal-brown` | `#191211` | `25, 18, 17` | Deep warm ink — primary dark text |
| `deep-regulatory-red` | `#710D0B` | `113, 13, 11` | Dark burgundy — strong headings, hover states |
| `regulatory-red` | `#C7372C` | `199, 55, 44` | Primary brand action — buttons, important highlights |
| `critical-red` | `#A61B14` | `166, 27, 20` | Critical finding — darker red for maximum contrast |
| `light-regulatory-red` | `#E05247` | `224, 82, 71` | Dark-theme primary red — brightened for dark backgrounds |
| `regulatory-red-muted` | `#C7372C15` | — | Red at 8% opacity — subtle highlight tints |
| `review-amber` | `#F58F1F` | `245, 143, 31` | Review required — warning status |
| `review-amber-muted` | `#F58F1F15` | — | Amber at 8% opacity |
| `compliant-green` | `#457534` | `69, 117, 52` | Compliant / verified status |
| `compliant-green-muted` | `#45753415` | — | Green at 8% opacity |
| `warm-graphite` | `#4A4743` | `74, 71, 67` | Secondary text |
| `stone-grey` | `#94938F` | `148, 147, 143` | Metadata, tertiary text |
| `clinical-mist` | `#D6D7D2` | `214, 215, 210` | Borders, dividers |
| `soft-stone` | `#F0F0EC` | `240, 240, 236` | Secondary surface, subtle backgrounds |
| `paper` | `#FAFAF7` | `250, 250, 247` | Main canvas — warm laboratory white |
| `document-white` | `#FFFFFF` | `255, 255, 255` | Document surface — crisp sheet white |
| `dark-surface` | `#292220` | `41, 34, 32` | Dark theme surface |
| `dark-elevated` | `#362D2A` | `54, 45, 42` | Dark theme elevated surface |
| `dark-canvas` | `#191211` | `25, 18, 17` | Dark theme canvas |

### 2.3 Semantic Tokens — Light Theme (Default)

| Semantic Token | Primitive | HEX | Usage |
|----------------|-----------|-----|-------|
| **Canvas & Surfaces** | | | |
| `--color-canvas` | `paper` | `#FAFAF7` | Application background — warm laboratory white |
| `--color-surface-primary` | `document-white` | `#FFFFFF` | Document reader, cards, panels, modals |
| `--color-surface-secondary` | `soft-stone` | `#F0F0EC` | Secondary surfaces, code blocks, sidebar background |
| `--color-surface-elevated` | `document-white` | `#FFFFFF` | Dropdowns, flyout menus (with shadow) |
| `--color-surface-document` | `document-white` | `#FFFFFF` | Document reading surface — the "sheet of paper" |
| `--color-surface-overlay` | `charcoal-brown` @ 40% | `#19121166` | Modal overlay backdrop |
| **Borders & Dividers** | | | |
| `--color-border-default` | `clinical-mist` | `#D6D7D2` | Card borders, input borders, table dividers |
| `--color-border-subtle` | `soft-stone` | `#F0F0EC` | Internal dividers, light separators |
| `--color-border-strong` | `stone-grey` | `#94938F` | Emphasized borders (document frame) |
| `--color-border-focus` | `regulatory-red` | `#C7372C` | Focus ring on interactive elements |
| `--color-border-brand` | `deep-regulatory-red` | `#710D0B` | Brand accent border (left edge of report header) |
| **Text** | | | |
| `--color-text-primary` | `charcoal-brown` | `#191211` | Headings, primary content, document text |
| `--color-text-secondary` | `warm-graphite` | `#4A4743` | Body text, descriptions, finding summaries |
| `--color-text-tertiary` | `stone-grey` | `#94938F` | Metadata, timestamps, helper text, captions |
| `--color-text-disabled` | `stone-grey` @ 50% | `#94938F80` | Disabled labels, inactive controls |
| `--color-text-inverse` | `document-white` | `#FFFFFF` | Text on red/dark buttons |
| `--color-text-brand` | `deep-regulatory-red` | `#710D0B` | Regulatory code references, brand-colored headings |
| **Brand & Interaction** | | | |
| `--color-brand-primary` | `regulatory-red` | `#C7372C` | Primary CTA button, active tab, focus ring |
| `--color-brand-hover` | `deep-regulatory-red` | `#710D0B` | Hover on primary actions |
| `--color-brand-pressed` | `#5A0908` | `#5A0908` | Pressed state on primary actions |
| `--color-brand-subtle` | `regulatory-red-muted` | `#C7372C10` | Subtle brand tint (selected sidebar item, active filter) |
| `--color-brand-text` | `deep-regulatory-red` | `#710D0B` | Brand-colored text links and references |
| **Semantic Status — Compliance Findings** | | | |
| `--color-finding-critical` | `critical-red` | `#A61B14` | Critical non-compliance finding |
| `--color-finding-critical-subtle` | `#A61B1412` | `#A61B1412` | Critical badge background tint |
| `--color-finding-major` | `review-amber` | `#F58F1F` | Major finding requiring remediation |
| `--color-finding-major-subtle` | `review-amber-muted` | `#F58F1F12` | Major badge background tint |
| `--color-finding-minor` | `stone-grey` | `#94938F` | Minor editorial recommendation |
| `--color-finding-minor-subtle` | `#94938F12` | `#94938F12` | Minor badge background tint |
| `--color-finding-compliant` | `compliant-green` | `#457534` | Fully compliant section |
| `--color-finding-compliant-subtle` | `compliant-green-muted` | `#45753412` | Compliant badge background tint |
| **Interactive States** | | | |
| `--color-hover-overlay` | `charcoal-brown` @ 3% | `#19121108` | Subtle hover on cards, rows, list items |
| `--color-active-overlay` | `charcoal-brown` @ 6% | `#19121110` | Active/pressed overlay |
| `--color-selected-bg` | `regulatory-red` @ 6% | `#C7372C10` | Selected row, active filter |
| **Document Annotations** | | | |
| `--color-annotation-highlight` | `regulatory-red` @ 8% | `#C7372C15` | Inline text highlight in document reader |
| `--color-annotation-underline` | `regulatory-red` @ 40% | `#C7372C66` | Underline for cited clauses |
| `--color-annotation-margin` | `regulatory-red` | `#C7372C` | Left-margin finding marker |

### 2.4 Semantic Tokens — Dark Theme

| Semantic Token | HEX | Usage |
|----------------|-----|-------|
| **Canvas & Surfaces** | | |
| `--color-canvas` | `#191211` | Deep warm charcoal canvas |
| `--color-surface-primary` | `#292220` | Cards, panels |
| `--color-surface-secondary` | `#221B19` | Sidebar, secondary areas |
| `--color-surface-elevated` | `#362D2A` | Dropdowns, modals |
| `--color-surface-document` | `#292220` | Document reading surface |
| `--color-surface-overlay` | `#19121180` | Modal backdrop |
| **Borders & Dividers** | | |
| `--color-border-default` | `#4A4743` | Card borders, inputs |
| `--color-border-subtle` | `#362D2A` | Internal dividers |
| `--color-border-strong` | `#5E5A57` | Emphasized borders |
| `--color-border-focus` | `#E05247` | Focus ring (brightened red) |
| `--color-border-brand` | `#C7372C` | Brand accent border |
| **Text** | | |
| `--color-text-primary` | `#F5F3EF` | Primary text |
| `--color-text-secondary` | `#C5C2BD` | Body text, descriptions |
| `--color-text-tertiary` | `#94938F` | Metadata, timestamps |
| `--color-text-disabled` | `#94938F50` | Disabled labels |
| `--color-text-inverse` | `#191211` | Text on light buttons |
| `--color-text-brand` | `#E05247` | Regulatory references (brightened for dark bg) |
| **Brand & Interaction** | | |
| `--color-brand-primary` | `#C7372C` | Primary CTA |
| `--color-brand-hover` | `#E05247` | Hover |
| `--color-brand-pressed` | `#A61B14` | Pressed |
| `--color-brand-subtle` | `#C7372C15` | Subtle brand tint |
| `--color-brand-text` | `#E05247` | Brand text links |
| **Semantic Status** | | |
| `--color-finding-critical` | `#E05247` | Critical (brightened) |
| `--color-finding-critical-subtle` | `#E0524715` | Critical tint |
| `--color-finding-major` | `#F58F1F` | Major |
| `--color-finding-major-subtle` | `#F58F1F15` | Major tint |
| `--color-finding-minor` | `#94938F` | Minor |
| `--color-finding-minor-subtle` | `#94938F15` | Minor tint |
| `--color-finding-compliant` | `#5A9A45` | Compliant (brightened) |
| `--color-finding-compliant-subtle` | `#5A9A4515` | Compliant tint |
| **Interactive** | | |
| `--color-hover-overlay` | `#FFFFFF06` | Hover |
| `--color-active-overlay` | `#FFFFFF0D` | Active |
| `--color-selected-bg` | `#C7372C12` | Selected |
| **Document Annotations** | | |
| `--color-annotation-highlight` | `#E0524720` | Highlight |
| `--color-annotation-underline` | `#E0524760` | Underline |
| `--color-annotation-margin` | `#E05247` | Margin marker |

### 2.5 Color Hierarchy Rules

```
┌─────────────────────────────────────────────────────────────────────┐
│  REGULATORY RED (#C7372C / #710D0B) — Brand & Critical Action      │
│                                                                     │
│  ✅ Primary CTA button fill                                         │
│  ✅ Active tab underline or indicator                                │
│  ✅ Focus ring on keyboard navigation                                │
│  ✅ Document annotation margin markers                               │
│  ✅ Regulatory reference text color (deep variant #710D0B)          │
│  ✅ Report cover accent rule                                         │
│  ✅ Finding card left-edge severity strip (critical)                 │
│  ✅ Brand accent in navigation (active item dot or underline)        │
│                                                                     │
│  ❌ Large page backgrounds or fills                                  │
│  ❌ Body text color (too low contrast on white at regular weight)    │
│  ❌ Card backgrounds                                                  │
│  ❌ Full-paragraph highlight fills                                    │
│  ❌ Decorative gradients                                              │
│  ❌ Generic error states (red must mean regulatory non-compliance)    │
├─────────────────────────────────────────────────────────────────────┤
│  COMPLIANT GREEN (#457534) — Verified Compliance                    │
│                                                                     │
│  ✅ "Compliant" finding badge                                        │
│  ✅ Verified section indicator in document sidebar                   │
│  ✅ Compliance score when high (e.g., >90%)                          │
│  ✅ Template section match confirmed                                 │
│                                                                     │
│  ❌ Branding element                                                  │
│  ❌ CTA button fill                                                   │
│  ❌ Navigation accent                                                 │
│  ❌ Decorative treatment                                              │
├─────────────────────────────────────────────────────────────────────┤
│  REVIEW AMBER (#F58F1F) — Attention Required                        │
│                                                                     │
│  ✅ Major finding badge (requires remediation within 30 days)        │
│  ✅ "Analysis in progress" indicator                                 │
│  ✅ Review-required document marker                                   │
│                                                                     │
│  ❌ Primary CTA (belongs to red)                                      │
│  ❌ Brand identity element                                            │
└─────────────────────────────────────────────────────────────────────┘
```

---

## 3. Spacing System

PharmaLens uses the same **8px base grid** as DeviationFlow for cross-product consistency, with generous spacing around document content to support comfortable reading.

### 3.1 Spacing Scale

| Token | Value | Usage |
|-------|-------|-------|
| `--space-0` | `0px` | No spacing |
| `--space-1` | `4px` | Micro: gap between icon and label in a tag |
| `--space-2` | `8px` | Tight: gap between inline elements, table cell compact |
| `--space-3` | `12px` | Compact: gap between stacked metadata, chip padding |
| `--space-4` | `16px` | Default: standard card padding, form field gap |
| `--space-5` | `20px` | Comfortable: gap between finding cards |
| `--space-6` | `24px` | Generous: modal body padding, section gap |
| `--space-8` | `32px` | Editorial: gap between major content sections |
| `--space-10` | `40px` | Large: document reader side margins |
| `--space-12` | `48px` | XL: page section vertical padding |
| `--space-16` | `64px` | XXL: hero section padding, report cover margins |

### 3.2 Document Reader Spacing

The document reader requires **wider margins and more generous spacing** than the application chrome.

| Property | Value | Rationale |
|----------|-------|-----------|
| **Document Container Max Width** | `780px` (including padding) | Constrains line length to ~72ch for optimal readability |
| **Document Side Padding** | `40px` left, `40px` right | Creates "margin" feel, like a printed document |
| **Paragraph Spacing** | `16px` bottom margin | Clear paragraph delineation |
| **Section Spacing** | `32px` top margin | Visual breathing room between document sections |
| **Annotation Margin Width** | `4px` left border | Left-edge finding markers |
| **Finding Sidebar Gap** | `24px` from document edge | Separation between document and audit panel |

### 3.3 Component Spacing Standards

| Component | Padding (internal) | Gap (between children) | Margin (external) |
|-----------|--------------------|------------------------|--------------------|
| **Finding Card** | `16px` all sides | `8px` between metadata rows | `12px` bottom (card-to-card) |
| **Document Section Card** | `20px` all sides | `12px` between sections | `0` (flush in reader) |
| **Table Row** | `10px` vertical, `16px` horizontal | — | `0` |
| **Table Header** | `8px` vertical, `16px` horizontal | — | `0` |
| **Button (Primary)** | `10px` vertical, `20px` horizontal | `8px` icon-to-label | `0` |
| **Button (Small)** | `6px` vertical, `12px` horizontal | `6px` icon-to-label | `0` |
| **Modal** | `24px` body, `20px` header/footer | `16px` between form fields | — |
| **Sidebar Navigation** | `12px` vertical, `16px` horizontal | `2px` between items | — |
| **Severity Chip** | `4px` vertical, `10px` horizontal | `4px` icon-to-text | `0` |
| **Form Input** | `10px` vertical, `14px` horizontal | — | `16px` bottom (field-to-field) |

---

## 4. Border & Radius System

### 4.1 Border Radius Scale

PharmaLens uses **restrained rounding** — the clinical aesthetic favors clean edges over playful pills.

| Token | Value | Usage |
|-------|-------|-------|
| `--radius-none` | `0px` | Table cells, inline code |
| `--radius-sm` | `4px` | Input fields, small buttons, tooltips |
| `--radius-md` | `6px` | Primary buttons, dropdowns |
| `--radius-lg` | `8px` | Cards, finding cards, panels |
| `--radius-xl` | `10px` | Modal dialogs |
| `--radius-2xl` | `12px` | Large floating panels, context panel |
| `--radius-full` | `999px` | Severity badges, compliance score circle |

### 4.2 Border Standards

```css
/* Document surface frame — the "sheet of paper" */
border: 1px solid var(--color-border-default);
border-radius: var(--radius-lg);

/* Finding card left-edge severity strip */
border-left: 3px solid var(--color-finding-critical);
border-radius: 0;

/* Focus ring — consistent across both products */
outline: 2px solid var(--color-border-focus);
outline-offset: 2px;
```

**Rules:**
- The document reading surface should feel like a **sheet of paper** — a white card with a subtle border, floating on the warm canvas.
- Finding cards use a **3px left border** colored by severity to create a scannable severity column.
- Never use colored full borders for status — use left-edge accent strips only.

---

## 5. Shadow & Elevation System

PharmaLens uses **softer, subtler shadows** than DeviationFlow. The light-first theme requires less dramatic elevation.

### 5.1 Elevation Levels

| Level | Token | Shadow Value (Light) | Shadow Value (Dark) | Usage |
|-------|-------|----------------------|---------------------|-------|
| **Level 0** | `--shadow-none` | `none` | `none` | Flush elements, table rows |
| **Level 1** | `--shadow-sm` | `0 1px 3px rgba(25, 18, 17, 0.06)` | `0 1px 2px rgba(0, 0, 0, 0.30)` | Cards, document surface |
| **Level 2** | `--shadow-md` | `0 4px 12px rgba(25, 18, 17, 0.08)` | `0 4px 12px rgba(0, 0, 0, 0.40)` | Dropdowns, flyout menus |
| **Level 3** | `--shadow-lg` | `0 8px 24px rgba(25, 18, 17, 0.10)` | `0 8px 24px rgba(0, 0, 0, 0.50)` | Modal dialogs |
| **Level 4** | `--shadow-xl` | `0 12px 40px rgba(25, 18, 17, 0.12)` | `0 16px 48px rgba(0, 0, 0, 0.60)` | Command palette |

**Rules:**
- Shadows in light theme use the warm `charcoal-brown` base (`#191211`) instead of pure black, producing warmer, more natural elevation.
- Prefer surface color differentiation (`--color-surface-secondary`) over shadows for subtle grouping.

---

## 6. Layout Architecture

### 6.1 Desktop Application Shell — Document-Centric Three-Zone Model

```
┌──────────────────────────────────────────────────────────────────────┐
│  ┌─────────────┐  ┌─────────────────────────────────┐  ┌─────────┐ │
│  │             │  │                                  │  │         │ │
│  │  DOCUMENT   │  │                                  │  │  AUDIT  │ │
│  │ NAVIGATION  │  │     DOCUMENT / COMPARISON        │  │ INTELLI-│ │
│  │             │  │                                  │  │  GENCE  │ │
│  │  Documents  │  │  Regulatory text with            │  │  PANEL  │ │
│  │  list       │  │  highlighted clauses and         │  │         │ │
│  │             │  │  annotation markers              │  │ Findings│ │
│  │  Sections   │  │                                  │  │ Risk    │ │
│  │  outline    │  │  Side-by-side diff view          │  │ Score   │ │
│  │             │  │  (document vs. template)         │  │ Actions │ │
│  │  Templates  │  │                                  │  │ Evidence│ │
│  │  list       │  │                                  │  │ History │ │
│  │             │  │                                  │  │         │ │
│  └─────────────┘  └─────────────────────────────────┘  └─────────┘ │
│      220–260px              flexible (1fr)              340–420px   │
│                              max: 780px content                     │
└──────────────────────────────────────────────────────────────────────┘
```

### 6.2 Zone Specifications

| Zone | Width | Background | Behavior |
|------|-------|------------|----------|
| **Document Navigation** | `220–260px` | `--color-surface-secondary` | Fixed left panel. Lists uploaded documents, template library, and section outline of currently viewed document. Collapsible. |
| **Document / Comparison** | `1fr` (fills remaining, content capped at `780px`) | `--color-canvas` (behind), `--color-surface-document` (the sheet) | Main scrollable document reader. Contains extracted text, highlighted clauses, and annotation markers. The document surface floats as a white "page" on the warm canvas. |
| **Audit Intelligence Panel** | `340–420px` | `--color-surface-primary` | Slide-in from right. Contains: compliance score, finding list by severity, corrective action recommendations, evidence links, analysis history. Dismissable. |

### 6.3 Document Reader — The "Sheet of Paper"

The central document view must feel like reading a **physical sheet** — a white card with generous margins floating on a warm canvas.

```
┌──────── Canvas (#FAFAF7) ───────────────────────────────────────────┐
│                                                                      │
│    ┌──────── Document Surface (#FFFFFF) ────────────────────────┐    │
│    │                                                            │    │
│    │   ▐ § 211.100(a) Production and Process Controls           │    │
│    │                                                            │    │
│    │   There shall be written procedures for production         │    │
│    │   and process control designed to assure that the          │    │
│    │   drug products have the identity, strength, quality,     │    │
│    │   and purity they purport or are represented to possess.  │    │
│    │                                                            │    │
│    │   ▐ This section discusses the requirement for             │    │  ← ▐ = Left margin
│    │   ▐ written production procedures that include all        │    │      annotation marker
│    │   ▐ relevant documentation references...                  │    │      (finding attached)
│    │                                                            │    │
│    │   ───────────────────────────────────────────              │    │
│    │                                                            │    │
│    │   § 211.100(b) Written production and process              │    │
│    │   control procedures shall be followed in the              │    │
│    │   execution of the various production and process          │    │
│    │   control functions...                                     │    │
│    │                                                            │    │
│    └────────────────────────────────────────────────────────────┘    │
│                                                                      │
│    max-width: 780px  |  padding: 40px  |  radius: 8px               │
│    shadow: --shadow-sm  |  border: 1px solid --color-border-default  │
│                                                                      │
└──────────────────────────────────────────────────────────────────────┘
```

---

## 7. Component Specifications

### 7.1 Buttons

| Variant | Background (Light) | Text | Border | Hover | Pressed | Usage |
|---------|--------------------|----- |--------|-------|---------|-------|
| **Primary** | `#C7372C` | `#FFFFFF` | None | `#710D0B` | `#5A0908` | "Run Analysis", "Upload Document", "Create Template" |
| **Secondary** | `transparent` | `#191211` | `1px solid #D6D7D2` | `#F0F0EC` | `#D6D7D2` | "Cancel", "Export", "Back" |
| **Ghost** | `transparent` | `#4A4743` | None | `#19121108` overlay | `#19121110` overlay | Inline actions, "View Details" |
| **Danger** | `#A61B14` | `#FFFFFF` | None | `#8A1510` | `#710D0B` | "Delete Document", "Remove Template" |
| **Disabled** | `#F0F0EC` | `#94938F` | None | — | — | Any disabled state |

**Dark theme adjustments:**

| Variant | Background | Text | Border | Hover |
|---------|------------|------|--------|-------|
| **Primary** | `#C7372C` | `#F5F3EF` | None | `#E05247` |
| **Secondary** | `transparent` | `#F5F3EF` | `1px solid #4A4743` | `#362D2A` |
| **Ghost** | `transparent` | `#C5C2BD` | None | `#FFFFFF08` |

**Button Sizing:** (identical to DeviationFlow for cross-product consistency)

| Size | Height | Padding | Font | Weight | Radius |
|------|--------|---------|------|--------|--------|
| **Small** | `32px` | `6px 12px` | Lato 13px | Bold 700 | `4px` |
| **Medium** | `40px` | `10px 20px` | Lato 14px | Bold 700 | `6px` |
| **Large** | `48px` | `12px 24px` | Lato 15px | Bold 700 | `6px` |

### 7.2 Finding Severity Badges

```
  ┌──────────────────┐  ┌──────────────────┐  ┌──────────────────┐  ┌──────────────────┐
  │ ⚠ CRITICAL        │  │ ◆ MAJOR          │  │ ○ MINOR          │  │ ✓ COMPLIANT      │
  └──────────────────┘  └──────────────────┘  └──────────────────┘  └──────────────────┘
   bg: #A61B1412         bg: #F58F1F12         bg: #94938F12         bg: #45753412
   text: #A61B14         text: #C96B00         text: #94938F         text: #457534
   left-strip: #A61B14   left-strip: #F58F1F   left-strip: #94938F   left-strip: #457534
```

| Property | Value |
|----------|-------|
| **Height** | `24px` |
| **Padding** | `4px 10px` |
| **Border Radius** | `999px` (pill) |
| **Font** | Lato, 11px, Bold 700, UPPERCASE |
| **Letter Spacing** | `+0.04em` |
| **Icon Size** | `12px`, positioned left with `4px` gap |

**Severity Icon Mapping:**

| Severity | Icon (Lucide) | Shape Language |
|----------|---------------|----------------|
| **Critical** | `AlertTriangle` | Triangle — universal danger |
| **Major** | `AlertCircle` | Circle with exclamation |
| **Minor** | `Info` | Circle with "i" |
| **Compliant** | `CheckCircle2` | Circle with check |

**Accessibility Rule:** Finding severity must use **triple encoding**:

```
[ICON SHAPE] + [TEXT LABEL] + [COLOR]

Example:
  ⚠ CRITICAL          ← Triangle icon + "CRITICAL" text + Red color
  ✓ COMPLIANT          ← Check icon + "COMPLIANT" text + Green color

Never:
  🔴                   ← Color alone — inaccessible
```

### 7.3 Compliance Score Display

The compliance score must be readable and meaningful **without color**.

```
┌──────────────────────────────────────────┐
│                                          │
│           94%                            │  ← Lato 48px Bold 700
│                                          │
│      High Compliance                     │  ← Lato 14px Bold 700
│                                          │
│  ┌────────────────────────────────────┐  │
│  │████████████████████████████░░░░░░░│  │  ← Progress bar
│  └────────────────────────────────────┘  │
│                                          │
│  12 sections checked                     │  ← Lato 13px Regular 400
│  2 critical · 1 major · 9 compliant     │  ← Lato 13px Regular 400
│                                          │
└──────────────────────────────────────────┘
```

| Score Range | Color | Label |
|-------------|-------|-------|
| `90–100%` | `--color-finding-compliant` | "High Compliance" |
| `70–89%` | `--color-finding-major` | "Moderate Compliance" |
| `0–69%` | `--color-finding-critical` | "Low Compliance" |

**Rule:** The **number and label** must be understandable without the progress bar or color. Color reinforces, it does not carry the information alone.

### 7.4 Document Annotations

Annotations mark clauses where the AI pipeline found findings. They must be **subtle and non-destructive** — the document content must remain the visual priority.

| Annotation Type | Visual Treatment | Usage |
|-----------------|------------------|-------|
| **Inline Highlight** | Background: `--color-annotation-highlight` (8% red) | Marks the specific text span linked to a finding |
| **Left Margin Marker** | `3px` left border: `--color-annotation-margin` | Indicates a finding is attached to this paragraph |
| **Clause Underline** | Bottom border: `1px dashed --color-annotation-underline` | Marks regulatory clause references |
| **Finding Badge (inline)** | Small pill positioned at end of highlighted span | Shows finding severity at a glance |

**Rules:**
- **Never** paint entire paragraphs with saturated background fills. Only highlight the specific relevant text span.
- Margin markers use a `3px` colored left border — consistent with finding card left-edge strips.
- Clicking an annotation scrolls the Audit Intelligence Panel to the corresponding finding.
- Clicking a finding in the panel scrolls the document to the corresponding annotation.

### 7.5 Form Inputs

| Property | Light Theme | Dark Theme |
|----------|-------------|------------|
| **Background** | `#FFFFFF` | `#292220` |
| **Border** | `1px solid #D6D7D2` | `1px solid #4A4743` |
| **Border (focus)** | `1px solid #C7372C` + `0 0 0 3px #C7372C25` | Same (using `#E05247`) |
| **Border (error)** | `1px solid #A61B14` + `0 0 0 3px #A61B1425` | Same (using `#E05247`) |
| **Text** | `#191211` (Arimo 14px 400) | `#F5F3EF` |
| **Placeholder** | `#94938F` (Arimo 14px 400) | `#94938F` |
| **Label** | `#191211` (Lato 13px 700) | `#F5F3EF` |
| **Helper** | `#94938F` (Lato 12px 400) | `#94938F` |
| **Error** | `#A61B14` (Lato 12px 700) | `#E05247` |
| **Height** | `40px` | `40px` |
| **Padding** | `10px 14px` | `10px 14px` |
| **Border Radius** | `4px` | `4px` |

### 7.6 Tables (Compliance Analysis History, Audit Records)

```
┌──────────────────────────────────────────────────────────────────────┐
│  DOCUMENT        │ TEMPLATE          │ SCORE  │ STATUS     │ DATE   │
│──────────────────┼───────────────────┼────────┼────────────┼────────│
│  SOP-QC-401.pdf  │ FDA cGMP          │ 94%    │ ✓ Complete │ 29 Sep │
│  BMR-2026-034.pdf│ ICH Q7            │ 72%    │ ◆ Review   │ 28 Sep │
│  VP-Clean-012.docx│ EU Annex 15      │ 88%    │ ✓ Complete │ 27 Sep │
└──────────────────────────────────────────────────────────────────────┘
```

| Property | Value |
|----------|-------|
| **Header Background** | `--color-surface-secondary` |
| **Header Font** | Lato, 11px, Bold 700, UPPERCASE, `--color-text-tertiary` |
| **Header Letter Spacing** | `+0.05em` |
| **Row Background (even)** | `--color-surface-primary` |
| **Row Background (odd)** | `--color-canvas` |
| **Row Hover** | `--color-hover-overlay` |
| **Row Selected** | `--color-selected-bg` |
| **Cell Font** | Arimo, 13px, Regular 400, `--color-text-secondary` |
| **Score Cell Font** | Arimo, 13px, SemiBold 600, `font-variant-numeric: tabular-nums` |
| **Row Height** | `44px` |
| **Cell Padding** | `10px 16px` |
| **Divider** | `1px solid --color-border-subtle` |

### 7.7 Modal Dialogs

| Property | Value |
|----------|-------|
| **Max Width** | `520px` (small), `680px` (medium), `860px` (large) |
| **Background** | `--color-surface-primary` |
| **Border** | `1px solid --color-border-default` |
| **Border Radius** | `10px` |
| **Header Padding** | `20px 24px` |
| **Body Padding** | `24px` |
| **Footer Padding** | `16px 24px` |
| **Overlay** | `--color-surface-overlay` |
| **Enter Animation** | `200ms ease-out` fade + scale from `0.95` |
| **Exit Animation** | `150ms ease-in` fade + scale to `0.97` |

---

## 8. Motion & Animation

### 8.1 Core Motion Principle

PharmaLens motion should feel **calm and analytical**. The product is an inspection environment, not a live operations console.

**Contrast with DeviationFlow:** Where DeviationFlow uses motion to communicate real-time state urgency (live pulses, stage transition flashes), PharmaLens uses motion only for spatial orientation (panels resizing, findings appearing, scores transitioning).

### 8.2 Timing Tokens

| Token | Duration | Easing | Usage |
|-------|----------|--------|-------|
| `--motion-instant` | `0ms` | — | Reduced motion fallback |
| `--motion-micro` | `100ms` | `ease-out` | Checkbox toggle, tooltip show |
| `--motion-fast` | `150ms` | `ease-out` | Button hover, chip selection |
| `--motion-default` | `200ms` | `ease-in-out` | Card hover, dropdown open |
| `--motion-moderate` | `300ms` | `ease-in-out` | Panel slide, modal appear, finding highlight |
| `--motion-slow` | `500ms` | `ease-in-out` | Score counter transition, document scroll-to |
| `--motion-reading` | `800ms` | `ease-in-out` | Compliance score dial animation on load |

### 8.3 Specific Motion Specs

| Interaction | Duration | Easing | Transform | Opacity |
|-------------|----------|--------|-----------|---------|
| **Card hover** | `150ms` | `ease-out` | — (background color change only) | — |
| **Finding card appear** | `250ms` | `ease-out` | `translateY(8px) → translateY(0)` | `0 → 1` |
| **Audit panel open** | `300ms` | `cubic-bezier(0.16, 1, 0.3, 1)` | `translateX(100%) → translateX(0)` | — |
| **Audit panel close** | `250ms` | `ease-in` | `translateX(0) → translateX(100%)` | — |
| **Modal enter** | `200ms` | `ease-out` | `scale(0.95) → scale(1)` | `0 → 1` |
| **Modal exit** | `150ms` | `ease-in` | `scale(1) → scale(0.97)` | `1 → 0` |
| **Document annotation highlight** | `300ms` | `ease-in-out` | — | `0 → 1` (background fade-in) |
| **Compliance score counter** | `800ms` | `ease-out` | Count from 0 to final value | — |
| **Score progress bar fill** | `600ms` | `ease-out` | Width `0% → final%` | — |
| **Document scroll-to-finding** | `500ms` | `ease-in-out` | Smooth scroll | — |
| **Dropdown open** | `150ms` | `ease-out` | `translateY(-4px) → translateY(0)` | `0 → 1` |
| **Sidebar collapse** | `250ms` | `ease-in-out` | Width `260px → 0px` | — |

### 8.4 Forbidden Motion

| ❌ DO NOT | Why |
|-----------|-----|
| Continuous pulsing indicators | PharmaLens is a reading/analysis environment, not an operations console |
| Flashing or blinking alerts | Creates visual noise during focused document review |
| Large sweeping entrance animations | Interrupts analytical focus |
| Parallax scrolling in document reader | Disorienting during regulatory text review |
| Auto-playing animated backgrounds | Competes with document content for attention |
| Score dial spinning on every re-render | Animate only on initial load or value change |

```css
@media (prefers-reduced-motion: reduce) {
  *, *::before, *::after {
    animation-duration: 0.01ms !important;
    animation-iteration-count: 1 !important;
    transition-duration: 0.01ms !important;
    scroll-behavior: auto !important;
  }
}
```

---

## 9. Iconography

### 9.1 Icon Library

**Primary:** Lucide React (consistent with DeviationFlow for cross-product consistency).

### 9.2 Icon Sizing Scale

| Token | Size | Stroke Width | Usage |
|-------|------|--------------|-------|
| `--icon-xs` | `14px` | `1.5px` | Inside severity chips, inline text |
| `--icon-sm` | `16px` | `1.5px` | Table actions, finding card actions |
| `--icon-md` | `20px` | `2px` | Button icons, navigation items |
| `--icon-lg` | `24px` | `2px` | Section header icons, page titles |
| `--icon-xl` | `32px` | `2px` | Empty state illustrations, dashboard stat cards |

### 9.3 Document & Compliance Icon Mapping

| Context | Icon (Lucide) | Usage |
|---------|---------------|-------|
| **Upload Document** | `Upload` | Upload button, drag-and-drop zone |
| **PDF File** | `FileText` | Document list item (PDF) |
| **DOCX File** | `FileType` | Document list item (DOCX) |
| **Template** | `ClipboardList` | Template list item |
| **Analysis Running** | `Loader2` (spinning) | Analysis in progress |
| **Analysis Complete** | `CheckCircle2` | Completed analysis |
| **Analysis Failed** | `XCircle` | Failed analysis |
| **Finding** | `AlertTriangle` / `AlertCircle` / `Info` / `CheckCircle2` | Per-severity finding |
| **Corrective Action** | `Wrench` | Recommended remediation |
| **Regulatory Reference** | `BookOpen` | CFR/ICH clause citation |
| **Audit Trail** | `History` | Audit log view |
| **Export** | `Download` | Export/download report |
| **Delete** | `Trash2` | Remove document/template |

---

## 10. Responsive Behavior

### 10.1 Breakpoints

| Token | Width | Behavior |
|-------|-------|----------|
| `--bp-desktop-xl` | `≥1440px` | Full three-zone layout, generous document margins |
| `--bp-desktop` | `≥1024px` | Three-zone layout, sidebar may be collapsed |
| `--bp-tablet` | `768–1023px` | Two-zone layout, audit panel becomes drawer |
| `--bp-mobile` | `<768px` | Single-zone sequential views |

### 10.2 Responsive Layout Strategy

**Desktop (≥1024px):**
- Full three-zone shell: Document Navigation + Document Reader + Audit Intelligence Panel
- Document reader uses full `780px` content width with generous margins
- Audit panel is a persistent sidebar

**Tablet (768–1023px):**
- Document navigation collapses to a slide-over drawer
- Document reader becomes full-width
- Audit intelligence panel becomes a slide-over drawer from the right
- Compliance score and critical findings remain visible in a compact top bar

**Mobile (<768px):**
- Do **not** attempt to reproduce the desktop document comparison view.
- Navigation becomes a bottom tab bar (Documents, Templates, Analyses, More)
- Document view becomes full-screen vertical scroll
- Findings appear as a bottom sheet overlay
- Prioritize: Document search → Upload → View analysis results → Critical findings
- Complex side-by-side diff analysis moves to sequential before/after views

---

## 11. Accessibility Standards

### 11.1 Color Contrast Requirements

| Combination (Light Theme) | Contrast Ratio | WCAG Level |
|---------------------------|----------------|------------|
| `#191211` on `#FFFFFF` | **18.2:1** | ✅ AAA |
| `#191211` on `#FAFAF7` | **17.4:1** | ✅ AAA |
| `#4A4743` on `#FFFFFF` | **9.5:1** | ✅ AAA |
| `#94938F` on `#FFFFFF` | **3.6:1** | ⚠️ AA Large Text Only |
| `#710D0B` on `#FFFFFF` | **10.8:1** | ✅ AAA |
| `#C7372C` on `#FFFFFF` | **5.5:1** | ✅ AA |
| `#FFFFFF` on `#C7372C` | **5.5:1** | ✅ AA |
| `#457534` on `#FFFFFF` | **6.0:1** | ✅ AA |

| Combination (Dark Theme) | Contrast Ratio | WCAG Level |
|--------------------------|----------------|------------|
| `#F5F3EF` on `#292220` | **13.4:1** | ✅ AAA |
| `#C5C2BD` on `#292220` | **8.2:1** | ✅ AAA |
| `#94938F` on `#292220` | **4.8:1** | ✅ AA |
| `#E05247` on `#292220` | **4.9:1** | ✅ AA |

**Note on `#94938F` (Stone Grey) in light theme:**  
At 3.6:1 on white, this color passes WCAG AA only for **large text** (≥18px or ≥14px bold). It should only be used for metadata captions, timestamps, and helper text — never for body content or interactive labels.

### 11.2 Reading Accessibility

| Guideline | Implementation |
|-----------|----------------|
| **Max line length** | Document reader content capped at `72ch` |
| **Min body font size** | `14px` for UI, `15px` for document text — never smaller for readable content |
| **Line height ratio** | ≥1.5 for body text, ≥1.4 for headings |
| **Paragraph spacing** | ≥`16px` between paragraphs |
| **Focus visible** | `2px solid #C7372C`, `outline-offset: 2px` — visible in both themes |
| **No text over images** | All text appears on solid surface backgrounds |
| **Resizable text** | Layout must not break at 200% browser zoom |

### 11.3 Keyboard Navigation

- All interactive elements reachable via `Tab`.
- Document annotations are focusable and navigable with `Tab` / `Shift+Tab`.
- Finding list items support `Arrow Up` / `Arrow Down` navigation.
- `Enter` opens finding detail, `Escape` closes panels/modals.
- Modal dialogs trap focus and restore on close.

### 11.4 Screen Reader Requirements

- All severity badges: `aria-label="Finding severity: Critical"`.
- Compliance score: `aria-label="Compliance score: 94 percent, High Compliance"`.
- Document annotations: `aria-describedby` linking to the corresponding finding ID.
- Analysis progress: `aria-live="polite"` with status updates.
- Upload zone: `aria-label="Upload document: Drag and drop or click to browse"`.

---

## 12. CSS Custom Properties — Implementation Reference

### 12.1 Light Theme Variables (`:root` / `[data-theme="light"]`)

```css
:root,
[data-theme="light"] {
  /* ── Canvas & Surfaces ── */
  --color-canvas: #FAFAF7;
  --color-surface-primary: #FFFFFF;
  --color-surface-secondary: #F0F0EC;
  --color-surface-elevated: #FFFFFF;
  --color-surface-document: #FFFFFF;
  --color-surface-overlay: rgba(25, 18, 17, 0.40);

  /* ── Borders ── */
  --color-border-default: #D6D7D2;
  --color-border-subtle: #F0F0EC;
  --color-border-strong: #94938F;
  --color-border-focus: #C7372C;
  --color-border-brand: #710D0B;

  /* ── Text ── */
  --color-text-primary: #191211;
  --color-text-secondary: #4A4743;
  --color-text-tertiary: #94938F;
  --color-text-disabled: rgba(148, 147, 143, 0.50);
  --color-text-inverse: #FFFFFF;
  --color-text-brand: #710D0B;

  /* ── Brand ── */
  --color-brand-primary: #C7372C;
  --color-brand-hover: #710D0B;
  --color-brand-pressed: #5A0908;
  --color-brand-subtle: rgba(199, 55, 44, 0.06);
  --color-brand-text: #710D0B;

  /* ── Finding Status ── */
  --color-finding-critical: #A61B14;
  --color-finding-critical-subtle: rgba(166, 27, 20, 0.07);
  --color-finding-major: #F58F1F;
  --color-finding-major-subtle: rgba(245, 143, 31, 0.07);
  --color-finding-minor: #94938F;
  --color-finding-minor-subtle: rgba(148, 147, 143, 0.07);
  --color-finding-compliant: #457534;
  --color-finding-compliant-subtle: rgba(69, 117, 52, 0.07);

  /* ── Interactive ── */
  --color-hover-overlay: rgba(25, 18, 17, 0.03);
  --color-active-overlay: rgba(25, 18, 17, 0.06);
  --color-selected-bg: rgba(199, 55, 44, 0.06);

  /* ── Document Annotations ── */
  --color-annotation-highlight: rgba(199, 55, 44, 0.08);
  --color-annotation-underline: rgba(199, 55, 44, 0.40);
  --color-annotation-margin: #C7372C;

  /* ── Typography ── */
  --font-display-primary: 'Maragsa', serif;
  --font-display-secondary: 'Arimo', sans-serif;
  --font-ui: 'Lato', sans-serif;
  --font-body: 'Arimo', sans-serif;

  /* ── Spacing ── */
  --space-1: 4px;
  --space-2: 8px;
  --space-3: 12px;
  --space-4: 16px;
  --space-5: 20px;
  --space-6: 24px;
  --space-8: 32px;
  --space-10: 40px;
  --space-12: 48px;
  --space-16: 64px;

  /* ── Radius ── */
  --radius-sm: 4px;
  --radius-md: 6px;
  --radius-lg: 8px;
  --radius-xl: 10px;
  --radius-2xl: 12px;
  --radius-full: 999px;

  /* ── Shadows ── */
  --shadow-sm: 0 1px 3px rgba(25, 18, 17, 0.06);
  --shadow-md: 0 4px 12px rgba(25, 18, 17, 0.08);
  --shadow-lg: 0 8px 24px rgba(25, 18, 17, 0.10);
  --shadow-xl: 0 12px 40px rgba(25, 18, 17, 0.12);

  /* ── Motion ── */
  --motion-micro: 100ms;
  --motion-fast: 150ms;
  --motion-default: 200ms;
  --motion-moderate: 300ms;
  --motion-slow: 500ms;
  --motion-reading: 800ms;
  --ease-default: ease-in-out;
  --ease-out: ease-out;
  --ease-in: ease-in;
  --ease-spring: cubic-bezier(0.16, 1, 0.3, 1);
}
```

### 12.2 Dark Theme Variables (`[data-theme="dark"]`)

```css
[data-theme="dark"] {
  /* ── Canvas & Surfaces ── */
  --color-canvas: #191211;
  --color-surface-primary: #292220;
  --color-surface-secondary: #221B19;
  --color-surface-elevated: #362D2A;
  --color-surface-document: #292220;
  --color-surface-overlay: rgba(25, 18, 17, 0.80);

  /* ── Borders ── */
  --color-border-default: #4A4743;
  --color-border-subtle: #362D2A;
  --color-border-strong: #5E5A57;
  --color-border-focus: #E05247;
  --color-border-brand: #C7372C;

  /* ── Text ── */
  --color-text-primary: #F5F3EF;
  --color-text-secondary: #C5C2BD;
  --color-text-tertiary: #94938F;
  --color-text-disabled: rgba(148, 147, 143, 0.50);
  --color-text-inverse: #191211;
  --color-text-brand: #E05247;

  /* ── Brand ── */
  --color-brand-primary: #C7372C;
  --color-brand-hover: #E05247;
  --color-brand-pressed: #A61B14;
  --color-brand-subtle: rgba(199, 55, 44, 0.10);
  --color-brand-text: #E05247;

  /* ── Finding Status ── */
  --color-finding-critical: #E05247;
  --color-finding-critical-subtle: rgba(224, 82, 71, 0.10);
  --color-finding-major: #F58F1F;
  --color-finding-major-subtle: rgba(245, 143, 31, 0.10);
  --color-finding-minor: #94938F;
  --color-finding-minor-subtle: rgba(148, 147, 143, 0.10);
  --color-finding-compliant: #5A9A45;
  --color-finding-compliant-subtle: rgba(90, 154, 69, 0.10);

  /* ── Interactive ── */
  --color-hover-overlay: rgba(255, 255, 255, 0.025);
  --color-active-overlay: rgba(255, 255, 255, 0.05);
  --color-selected-bg: rgba(199, 55, 44, 0.08);

  /* ── Document Annotations ── */
  --color-annotation-highlight: rgba(224, 82, 71, 0.12);
  --color-annotation-underline: rgba(224, 82, 71, 0.40);
  --color-annotation-margin: #E05247;

  /* ── Shadows ── */
  --shadow-sm: 0 1px 2px rgba(0, 0, 0, 0.30);
  --shadow-md: 0 4px 12px rgba(0, 0, 0, 0.40);
  --shadow-lg: 0 8px 24px rgba(0, 0, 0, 0.50);
  --shadow-xl: 0 16px 48px rgba(0, 0, 0, 0.60);
}
```

---

## 13. Information Density Modes

| Density Level | Row Height | Card Padding | Font Size Base | Usage |
|---------------|------------|--------------|----------------|-------|
| **Comfortable** | `56px` | `24px` | `15px` | Document reading, compliance reports, onboarding |
| **Standard** | `44px` | `16px` | `14px` | Default workspace, finding cards, forms |
| **Dense** | `36px` | `12px` | `13px` | Analysis history tables, audit log, regulatory reference lists |

---

## 14. Empty States

Empty states use the **Maragsa brand font** to create warm, scholarly editorial moments.

```
┌──────────────────────────────────────────────────────────────┐
│                                                              │
│                                                              │
│           NO ANALYSES YET.                                    │
│           ────────────────                                    │
│           Maragsa, 40px                                       │
│                                                              │
│           Upload a document and select a compliance           │
│           template to run your first regulatory audit.        │
│           ──────────────────────────────────────────          │
│           Arimo, 15px, --color-text-secondary                 │
│                                                              │
│                   [ Upload Document ]                         │
│                   Primary CTA Button (Lato 14px 700)          │
│                                                              │
└──────────────────────────────────────────────────────────────┘
```

---

## 15. Alternative Brand Font Pairs — Approved Secondary Identities

### 15.1 Brasika + Lato — Campaign & Promotional

| Font | Context |
|------|---------|
| **Brasika** (Display) | Campaign landing pages, feature announcements, product launch hero, marketing banners |
| **Lato** (Supporting) | All supporting text in marketing contexts |

**Why secondary:** Brasika is more expressive and promotional than Maragsa. PharmaLens's primary brand identity benefits from Maragsa's scholarly restraint for the core product. Brasika is reserved for outward-facing campaign moments.

### 15.2 Kelin Eator + Red Hat Display — Editorial Features

| Font | Context |
|------|---------|
| **Kelin Eator** (Display) | Special editorial feature pages, product storytelling, thought leadership content, large feature headings |
| **Red Hat Display** (Supporting) | Supporting copy, UI headings, navigation, buttons |

**Why secondary:** Kelin Eator is visually distinctive enough that frequent use can overpower dense enterprise interfaces. It works best for intentional editorial moments.

### 15.3 Font Assignment Matrix

| Context | Primary Display | Supporting Display | UI Font | Body / Document |
|---------|----------------|--------------------|---------|-----------------|
| **Product Core** | Maragsa | Arimo (display weight) | Lato | Arimo |
| **Marketing / Campaign** | Brasika | Lato | Lato | Lato |
| **Editorial / Feature** | Kelin Eator | Red Hat Display | Red Hat Display | Arimo |

**Key Principle:** These four display families are **never competitors** on the same screen. Each has a clear, exclusive role.

---

## 16. Cross-Product Design Consistency (PharmaLens ↔ DeviationFlow)

While PharmaLens and DeviationFlow have distinct visual identities, they share structural design DNA as products from the same design family:

| Shared Element | Specification |
|----------------|---------------|
| **Spacing Scale** | Same 8px/4px grid, same spacing token names |
| **Radius Scale** | Same radius token values (4px, 6px, 8px, 10px, 12px, 999px) |
| **Icon Library** | Both use Lucide React |
| **Button Sizing** | Same height/padding matrix (32px, 40px, 48px) |
| **Modal Structure** | Same width tiers (520, 680, 860px), same enter/exit animation timing |
| **Table Structure** | Same header typography treatment, same row heights |
| **Accessibility Rules** | Same triple-encoding severity standard, same keyboard navigation patterns |
| **Motion Timing Tokens** | Same token names and base durations |
| **Status Semantics** | Both share `Compliant Green (#457534)`, `Review Amber (#F58F1F)`, and critical red |

| Distinct Element | DeviationFlow | PharmaLens |
|-----------------|---------------|------------|
| **Default Theme** | Dark-first | Light-first |
| **Brand Color** | Tangerine `#F58F1F` | Regulatory Red `#C7372C` |
| **Display Font** | Lava Pro Rough (industrial) | Maragsa (editorial serif) |
| **UI Font** | Red Hat Display | Lato |
| **Canvas Feel** | Dark graphite control room | Warm laboratory paper |
| **Motion Character** | Kinetic, signal-driven (pulses, flashes) | Calm, analytical (fades, scrolls) |
| **Primary Metaphor** | Mission control console | Regulatory reading room |

---

## 17. Design Decision Log

| Decision | Rationale |
|----------|-----------|
| **Light-first theme** | PharmaLens's primary task is reading and comparing regulatory documents. A warm light canvas (`#FAFAF7`) reduces cognitive friction during multi-hour reading sessions, compared to dark surfaces that can cause halation around dense text. |
| **Maragsa restricted to display contexts** | Its high-contrast editorial serif character is powerful at large sizes but would reduce readability and create visual fatigue when used for dense compliance tables, form labels, or finding descriptions. |
| **Separate fonts for application chrome (Lato) vs. document content (Arimo)** | Creates an immediate visual boundary between "the tool" and "the material being inspected." Users can distinguish interface controls from source document text without needing borders or background colors. |
| **Document reader as "sheet of paper"** | The white document surface floating on a warm canvas creates a physical metaphor that grounds the reading experience. It feels like reviewing a printed document, which builds trust in regulatory contexts. |
| **Regulatory red used surgically** | Red carries inherent semantic weight (non-compliance, failure). If applied as large decorative fills, it would create visual panic. Instead, red appears as brand accents (borders, links, buttons) in safe contexts and as severity indicators only in compliance contexts. |
| **Annotations use underlines and margin markers, not full-paragraph fills** | Saturated background fills destroy the readability of the underlying document text. Subtle underlines and left-margin markers preserve the reading experience while clearly indicating where findings are attached. |
| **Shadows use warm charcoal base in light theme** | Pure black shadows (`rgba(0,0,0)`) feel cold and detached on a warm canvas. Using `rgba(25, 18, 17)` (the charcoal-brown primitive) produces warmer, more natural elevation that matches the warm paper aesthetic. |
| **Dark theme uses warm brown-blacks, not neutral grays** | PharmaLens's dark theme should feel like a private regulatory reading room — warm, intimate, and focused — not a developer IDE. The warm brown-tinged dark surfaces (`#191211`, `#292220`, `#362D2A`) achieve this. |
| **Compliance score requires number + label + bar** | Color-only scores fail for colorblind users. The score must be fully comprehensible through its number ("94%") and text label ("High Compliance") without seeing the progress bar color. |

---

> **End of PharmaLens Design System Specification.**  
> All frontend implementation — CSS custom properties, component styling, document reader layout, responsive behavior, and motion — must conform to this document.
