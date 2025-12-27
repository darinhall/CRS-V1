## Spec pipeline implementation plan (core + product specializations)

This document is the **master implementation plan** for finishing `backend/src/agents/spec_pipeline/` into a scalable ingestion system.

It is intentionally aligned with:

- the DB-first model in `backend/src/agents/spec_pipeline/format.md`
- the existing Playwright scaffolding in `backend/src/agents/spec_pipeline/core/discovery_agent.py` and `backend/src/agents/spec_pipeline/core/extraction_agent.py`
- the stronger Canon crawling patterns in `src/website_scrapers/canon_scraper.py`

This is written for **iteration speed** first (hardcoded config files), then production hardening.

---

## Guiding principles (non-negotiables)

- **Contract-first**: every stage emits the shapes described in `format.md` (Discovery → Extraction → Normalization → Validation → Persistence).
- **Deterministic extraction** first: HTML/PDF parsing should be tools + parsers. LLMs are reserved for ambiguous mapping and review assistance.
- **DB rules before LLM**: use `spec_mapping` (DB table) to map raw keys → `spec_definition`. LLM proposes new mappings only when no rule matches.
- **Never guess**: if a value cannot be verified from a source artifact, do not fabricate it; emit a TODO/flag with low confidence.
- **Matrix/table specs** must go into `product_spec_matrix` (plus a parent `product_spec` + provenance JSONB).

---

## Target folder structure

### `spec_pipeline/core/` (shared infrastructure)

Create these modules (some already exist; some are TODO):

- `contracts.py`
  - dataclasses/pydantic models for the agent output contract (the JSON shapes from `format.md`)
  - validation helpers: “is this output contract-valid?”

#### Extraction layer (keep it simple: 2 files to start)

Start with just **two core files**:

- `discovery.py`
  - URL discovery + pagination + bot avoidance + URL inventory JSON output
  - implement multiple classes inside this file as needed (e.g., `CanonDiscovery`, `SonyDiscovery`)

- `extraction.py`
  - product page extraction (HTML) + PDF link detection + (later) PDF table extraction
  - implement multiple classes inside this file as needed (e.g., `CanonProductExtractor`, `PdfExtractor`)

This keeps iteration fast while still separating concerns.

**Important:** even with only two files, keep functions/classes separated by concern internally:

- discovery ≠ extraction
- web extraction ≠ pdf extraction ≠ ocr fallback (can live in the same file as separate classes)

Later refactor option (only if it grows too big): split into `extractors/` package modules (`web.py`, `pdf.py`, `ocr.py`).

- `mappers.py`  **(new)**
  - DB rule mapping (loads `spec_mapping` + `spec_definition`)
  - LLM fallback to propose new mappings (creates review suggestions, does not auto-commit)
  - emits **Normalization output** records

- `validators.py`  **(new / merge with existing `validator.py`)**
  - JSONSchema validation (structure)
  - semantic validation (units, ranges, impossible values)
  - matrix completeness checks (e.g., expected aspect ratio columns exist)
  - emits **Validation output**

- `persistence.py`  **(new)**
  - DB upsert routines (psycopg2):
    - upsert product by slug
    - upsert specs by `(product_id, spec_definition_id)`
    - upsert matrix cells by `(product_id, spec_definition_id, dims)`
  - emits **Persistence output**

- `orchestrator.py`  **(new)**
  - simple stage runner: extract → normalize → validate → persist
  - optional enrichment stage behind config flag
  - metrics + “review queue” collection

- `discovery_agent.py`  **(exists)**
  - keep, but upgrade to Canon-grade discovery logic using patterns from `canon_scraper.py`

- `extraction_agent.py`  **(exists)**
  - keep, but refactor parsing into strategy objects under `extractors.py`

- `utils.py`  (exists, currently empty)
  - shared helpers: slugify, retry/backoff, timing, structured logging, HTML cleanup

### `spec_pipeline/product/<type>/` (product-specific overrides)

Each product type is a thin specialization layer (do NOT re-implement the 5 stages):

- `taxonomy.py`
  - canonical sections + tier-1 keys for UI (filters/compare/graphs)
  - section ordering rules

- `extractor.py`
  - manufacturer-specific DOM selectors/table parsers unique to this product type
  - PDF table parsers for this type (matrix/kv tables)

- `mappings.py`
  - seedable mapping rules/synonyms
  - optionally exports a function that writes `spec_mapping` rules into DB (or generates SQL)

- `validators.py`
  - type-specific semantic checks (e.g., cameras: shutter speed constraints; lenses: focal length ranges)

- `pipeline.py`
  - factory that wires core orchestrator + product-specific config into a runnable pipeline object

---

## Runner workflow (hardcoded configs first)

### Why hardcoded configs for iteration

You want fast iteration on ingestion logic. Start with simple “edit config file, run pipeline” flows.
Later you can add CLI arguments and/or environment toggles.

### Add a single runner

Create one entrypoint file (recommended location):

- `backend/main.py` (or `backend/scripts/run.py`)

Runner responsibilities only:

- load `.env`
- choose local vs cloud DB URL
- open psycopg2 connection
- pick a product pipeline factory (camera/lens/tripod)
- call `pipeline.run(config)`

Runner should NOT:

- contain scraping logic
- contain mapping logic
- contain SQL upsert statements (those belong in `persistence.py`)

### Hardcoded config files

Add a folder:

- `backend/src/agents/spec_pipeline/config/`

And create files like:

- `camera_canon_dev.py`
  - brand slug, category slug
  - listing URLs
  - product URL pattern
  - max products to process
  - headless toggle
  - feature flags:
    - enable_enrichment
    - enable_llm_fallback_mapping
    - save_raw_html
    - save_pdf_assets
    - pdf_policy (see below)

This keeps early iteration simple while your pipeline stabilizes.

---

## Step-by-step implementation plan (phased)

### Phase 0 — Align names and remove ambiguity

- Ensure all DB code uses singular table names:
  - `brand`, `product_category`, `spec_section`, `spec_definition`, `spec_mapping`, `product`, `product_spec`, `product_spec_matrix`
- Ensure schema concepts match the contract:
  - `product_spec.raw_value_jsonb` used for provenance blobs
  - `product_spec_matrix.dims` JSONB used for matrix dimensions

Watch-outs:

- avoid PL/pgSQL variable naming collisions (use `v_product_id` etc.)
- avoid denormalized `spec_key/spec_section` duplication in `product_spec`

### Phase 1 — Discovery (Canon-grade URL crawling)

Goal: reliably produce URL inventories keyed by product type.

Implementation details (borrow from `src/website_scrapers/canon_scraper.py`):

- URL pagination:
  - try `?p=2,3,...` pagination first
  - fallback to “Load more” button clicking
- bot avoidance:
  - realistic headers + viewport
  - randomized delays + longer breaks
- URL filtering:
  - include `/shop/p/` only
  - exclude query strings (`?`)
  - exclude “refurbished”

Output format:

- write a JSON file per brand+product type:
  - `data/url_lists/{brand}_{product_type}_urls.json`
  - include metadata: discovery_date, total_urls, listing URLs used
  - optionally include category slug and “pipeline id”

Also produce a **PDF download inventory** when PDFs are detected (see Phase 2/3).

### Phase 2 — Extraction (web)

Goal: turn each product URL into `manufacturer_sections` + raw artifacts.

Work required:

- refactor `core/extraction_agent.py` so table extraction returns structured data, not placeholder strings
- implement Canon DOM parsing strategy:
  - primary: `div#tech-spec-data` with `.tech-spec-attr` pairs (already present)
  - table handling:
    - extract header row(s)
    - extract cell grid
    - emit as `tables[]` in the extraction output

#### Canon-specific PDF policy (as requested)

For Canon cameras:

- **PDF is used only if web is missing** (or below a completeness threshold you define).
- Extraction should always check for PDF/manual/spec links during web extraction.

Implementation detail:

- During web extraction, collect any PDF links into a “download queue” JSON file so you can manually download them if needed.

Example output (write to `data/pdf_queue/{brand}_{product_type}_pdf_queue.json`):

```json
{
  "brand": "canon",
  "product_type": "camera",
  "generated_at": "2025-12-23T00:00:00Z",
  "items": [
    {
      "product_slug_hint": "eos-r6-mark-iii",
      "product_url": "https://www.usa.canon.com/shop/p/eos-r6-mark-iii",
      "pdf_url": "https://www.usa.canon.com/…/some-spec-sheet.pdf",
      "pdf_kind": "spec_sheet",
      "reason": "web_missing_specs",
      "status": "needs_download"
    }
  ]
}
```

After manual download, you place PDFs into a predictable local folder, e.g.:

- `data/pdfs/canon/camera/eos-r6-mark-iii/spec_sheet.pdf`

Then Phase 3 can run deterministically using local paths.

Output contract compliance:

- include section name (`h3` group headers)
- include raw key label, raw value (verbatim)
- for tables: include enough structure for downstream conversion into `product_spec_matrix`

### Phase 3 — Extraction (PDF)

Goal: reliably pull tables and key/value specs from PDFs/manuals.

Approach:

- deterministic extraction with a library (choose one):
  - `pdfplumber` for table-ish extraction
  - `camelot`/`tabula` for strong table extraction when PDFs are well-structured
  - OCR fallback only for scanned PDFs

#### Tying PDF parsing into LangChain (correct way)

Do **not** ask the LLM to “read the PDF” directly. Instead:

- write deterministic extractors (`pdfplumber`/`camelot`) that output structured JSON (tables/kv blocks)
- optionally wrap those extractors as LangChain **tools** so an LLM can:
  - choose which table to parse next
  - label a table (“still image recording pixels”)
  - propose dimension keys / mapping suggestions

But the parsing itself remains deterministic and testable.

Output:

- produce `matrix_records[]` where applicable
- attach provenance:
  - page number
  - table title/heading
  - notes/footnotes extracted (important for “rounded values”, “inexact proportion”, etc.)

### Phase 4 — Normalization + Mapping

Goal: map raw keys → canonical `normalized_key`, parse values into typed columns, and produce DB-ready records.

Rules:

- first attempt mapping via DB `spec_mapping` rules:
  - key regex + optional context regex
  - priority-based tie-breaking
- only if unmapped:
  - LLM proposes a mapping (secondary tool):
    - suggested normalized_key
    - confidence
    - rationale + example context
  - do NOT auto-insert low-confidence mappings into DB

#### Where LangChain should be used (and where it should NOT)

Use LangChain primarily for **mapping/normalization** and human-review support:

- **Primary**:
  - propose new `normalized_key` matches when DB rules fail
  - propose units/range parsing for tricky strings (optional)
  - generate “review queue” suggestions

Avoid LangChain for bulk extraction:

- do not feed full HTML pages into an LLM for table extraction at scale
- do not feed raw PDFs into an LLM as the primary parser

This keeps cost predictable and output stable.

Parsing:

- parse numbers/ranges/booleans deterministically
- store `unit_used` (including “stops”)
- keep `raw_value` verbatim
- store `raw_value_jsonb` only for structured provenance

Matrix normalization:

- parent record:
  - `normalized_key = <matrix key>`
  - `spec_value = "See product_spec_matrix"`
  - `raw_value_jsonb` describes dimension keys and notes
- cell rows:
  - write to `product_spec_matrix` with `dims` JSONB and typed fields

### Phase 5 — Validation/QA

Goal: prevent garbage-in at scale.

Three tiers:

- structural validation (contract schema)
- semantic validation (units, numeric ranges, required tier-1 keys)
- matrix validation (expected dimension keys present; no impossible combinations)

Outputs:

- `errors[]`: block persistence
- `warnings[]`: persist but flag for review
- `flagged_for_review[]`: suggested new mappings and low-confidence values
- `quality_score`

### Phase 6 — Persistence

Goal: safe, idempotent writes.

DB upsert plan:

- upsert `product` by `slug`
- upsert `product_spec` by `(product_id, spec_definition_id)`
- upsert `product_spec_matrix` by `(product_id, spec_definition_id, dims)`
- commit in batches (transaction per product or per N products)
- log counts and conflicts

### Phase 7 — UI-friendly views (optional but recommended)

Add views for common access patterns:

- matrix “grid view” (already done for still image recording pixels)
- compare payload JSON per product
- grouped accordion payload JSON per product

---

## Class/file renames and cleanup targets

These are conceptual cleanups to apply during refactor:

- `SourceExtractorAgent` → `Extractor` (deterministic) + optional `LLMInterpreter`
  - avoid LLM-driven extraction as the default

- `TerminologyMapperAgent` → `Mapper` / `Normalizer`
  - DB rule mapping first; LLM fallback to propose new mappings

- `SchemaValidatorAgent` → `Validator`
  - keep deterministic; LLM only for explanation/triage if needed

- `EnrichmentAgent` remains, but behind a feature flag; default off.

- `SpecNormalizationOrchestrator` → `PipelineOrchestrator`
  - orchestrates stage modules; no embedded parsing logic

---

## Known issues we already hit (carry forward as warnings)

- **psql meta-commands in migrations**: `\set`, `\ir` break Supabase migrations; migrations must be pure SQL.
- **Docker daemon** must be running for local Supabase: `supabase start` requires Docker.
- **ambiguous PL/pgSQL variables**: avoid naming variables same as column names.
- **denormalized fields drift**: do not store `spec_key/spec_section` on `product_spec`.
- **tables/matrices**: do not store table data in a single `spec_value` string; always normalize to `product_spec_matrix`.

---

## Deliverables checklist (what “done” looks like)

- Core pipeline:
  - [ ] `contracts.py` defines the JSON contract with validation helpers
  - [ ] `extractors.py` supports Canon web extraction + table extraction
  - [ ] `mappers.py` supports DB rule mapping + LLM fallback proposals
  - [ ] `validators.py` runs structural + semantic + matrix QA
  - [ ] `persistence.py` writes to DB idempotently
  - [ ] `orchestrator.py` wires stages and produces a run report

- Product pipelines:
  - [ ] `product/camera/pipeline.py` and equivalents exist
  - [ ] product-specific mapping seeds exist (`mappings.py`)
  - [ ] product-specific validators exist (`validators.py`)

- Runner:
  - [ ] one runner file loads hardcoded config and runs a pipeline end-to-end

- Evidence:
  - [ ] local Supabase reset completes and seeds data
  - [ ] pipeline can ingest at least 1 Canon product end-to-end
  - [ ] at least one matrix spec is ingested and view query works

