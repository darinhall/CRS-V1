## Spec pipeline implementation plan (core + plugin specializations)

This document is the **master implementation plan** for finishing `backend/src/agents/spec_pipeline/` into a scalable ingestion system.

It is intentionally aligned with:

- the DB-first model in `backend/src/agents/spec_pipeline/format.md`
- the robust Canon crawling patterns in `src/website_scrapers/canon_scraper.py`

This is written for **iteration speed** first, while keeping an obvious path to scaling across **many brands** and **many product types**.

---

## Short “why we changed” note (migration)

We moved away from “6 files per brand per product type” (e.g. `canon_discovery.py`, `canon_extractor.py`, …) because that explodes into hundreds of tiny modules and makes refactors painful.

Instead we use a **hybrid model** + **minimal plugin modules**:

- **Product type first** (cameras vs lenses behave differently)
- **Brand plugins inside that type** (Canon camera ≠ Sony camera)
- **One `plugin.py` per brand+type** (start minimal; split later only if needed)

---

## Guiding principles (non-negotiables)

- **Contract-first**: every stage emits the shapes described in `format.md` (Discovery → Extraction → Normalization → Validation → Persistence).
- **Deterministic extraction first**: HTML/PDF parsing should be tools + parsers. LLMs are reserved for ambiguous mapping and review assistance.
- **DB rules before LLM**: use `spec_mapping` (DB table) to map raw keys → `spec_definition`. LLM proposes new mappings only when no rule matches.
- **Never guess**: if a value cannot be verified from a source artifact, do not fabricate it; emit a TODO/flag with low confidence.
- **Matrix/table specs** must go into `product_spec_matrix` (plus a parent `product_spec` + provenance JSONB).

---

## Folder taxonomy (hybrid model)

### 1) `spec_pipeline/core/` (shared infrastructure)

Core holds stable contracts + shared primitives:

- discovery primitives (pagination, filtering, output shape validation)
- extraction primitives
- registry/loader for “which plugin do I run?”

### 2) `spec_pipeline/product/<type>/<brand>/` (brand+type plugins)

This is where most implementation lives.

Example:

- `spec_pipeline/product/camera/canon/plugin.py`
- `spec_pipeline/product/camera/sony/plugin.py`
- `spec_pipeline/product/lens/canon/plugin.py`

Start minimal: **one file per brand+type**.
When (and only when) the plugin grows too large, split into `discovery.py`, `extractor.py`, etc. inside that brand folder.

### 3) Optional `spec_pipeline/brand/<brand>/` (shared brand helpers)

Only introduce this when you find real cross-type reuse for a brand, e.g.:

- Canon “shop client” / cookie logic shared by camera and lens discovery

---

## Minimal plugin contract (initial)

Each `plugin.py` should export:

- `BRAND_SLUG`: `str`
- `PRODUCT_TYPE`: `str`
- `DISCOVERY_CONFIG`: `DiscoveryConfig` (hardcoded dev config for now)
- optional future exports:
  - `extract(product_url) -> ExtractionOutput`
  - `normalize(extraction) -> NormalizationOutput`
  - `validate(records) -> ValidationOutput`
  - `persist(records) -> PersistenceOutput`

---

## Runner workflow (hardcoded default + CLI overrides)

We support **both**:

- **Hardcoded default**: fastest dev loop (no flags required)
- **CLI overrides**: scalable (same runner can execute any plugin)

Important: runner selection style is **separate** from Supabase migration workflow.
Migrations are for schema/baseline seeds; the runner is for runtime ingestion.

---

## Discovery-only data flow (today)

```mermaid
flowchart TD
  Runner[backend/scripts/run.py] -->|"defaults_or_cli"| Registry[core/registry.py]
  Registry --> Plugin[product/camera/canon/plugin.py]
  Plugin --> DiscoveryCore[core/discovery.py]
  DiscoveryCore --> UrlInventory[data/url_lists/canon_camera_urls.json]
```

---

## Current implementation status (what we built so far)

This section documents the **exact working pipeline** we implemented for Canon mirrorless cameras, including where files are written and how the DB-driven mapping loop improves over time.

### Canon camera plugin entrypoint

- Plugin: `backend/src/agents/spec_pipeline/product/camera/canon/plugin.py`
- It currently supports three runnable stages via `backend/scripts/run.py`:
  - `--stage discovery`
  - `--stage extraction`
  - `--stage normalize`

### Stage 1: Discovery (URL inventory JSON)

**Code**
- Discovery implementation: `backend/src/agents/spec_pipeline/core/discovery.py`
- Canon plugin config: `DISCOVERY_CONFIG` in `product/camera/canon/plugin.py`
- Registry: `backend/src/agents/spec_pipeline/core/registry.py`

**Filters implemented**
- include `/shop/p/` only
- exclude query strings (`?`) and refurbished
- strip URL fragments (e.g. `#toreviews`) for dedupe
- exclude slug substrings:
  - `kit`
  - `with-cropping-guide-firmware`
  - `with-stop-motion-animation-firmware`

**Output**
- `data/url_lists/canon_camera_urls.json`

**Run**
```bash
python3 backend/scripts/run.py --stage discovery
```

### Stage 2: Extraction (HTML → manufacturer_sections)

**Code**
- Extractor: `backend/src/agents/spec_pipeline/core/extraction.py`
- Canon extraction config: `EXTRACTION_CONFIG` in `product/camera/canon/plugin.py`

**Inputs**
- For Canon, we prefer your on-disk HTML cache:
  - reads `data/company_product/canon/raw_html/{slug}.html`
  - `cache_only=true` means “do not hit the network if missing”

**Outputs**
- Extraction JSON:
  - `data/company_product/canon/processed_data/camera/extractions.json`
- Optional fetched HTML artifact folder (only used if cache fallback is enabled):
  - `data/company_product/canon/processed_data/camera/raw_html/`

**PDF links captured**
- If a spec attribute contains a PDF link, extraction stores:
  - `context.pdf_url`

**Completeness heuristics**
- Each item includes `completeness` (sections/attributes/tables/pdf_urls_found + `needs_pdf` flag).
  - This is used to identify products where Canon HTML is incomplete or absent.

**Run**
```bash
python3 backend/scripts/run.py --stage extraction
```

### Product documents: persist PDF URLs as rows (Option B)

We store PDF URLs in a dedicated table so they’re queryable and trackable (download/parse status).

**DB**
- Table: `product_document`
- Migration: `supabase/migrations/20251228000000_add_product_document.sql`
- Schema mirror: `backend/db/schema.sql`

**Import**
- Importer script: `backend/scripts/import_documents_from_extractions.py`

Run (local example):
```bash
export DATABASE_URL="postgresql://postgres:postgres@127.0.0.1:54322/postgres"
python3 backend/scripts/import_documents_from_extractions.py
```

### Stage 3: Normalization + Mapping (DB-driven)

**Code**
- Normalizer: `backend/src/agents/spec_pipeline/core/normalization.py`
- Text cleanup (display-facing): `backend/src/agents/spec_pipeline/core/text_normalizer.py`
- Mapping engine: `backend/src/services/spec_mapper.py`

**Important policies**
- Preserve `raw_value` verbatim for provenance.
- Compute a cleaned `spec_value` for UI display (bullet/spacing normalization).
- Do not treat PDF links as specs:
  - they are emitted as `documents[]` in normalized output
  - and persisted into `product_document` via importer
- Table placeholders remain as `table_records[]` for now; matrix conversion is a later milestone.
  - Exception: we now convert the Canon **Still Image \"File Size\"** table into `matrix_records[]` + `matrix_cells[]` as the first concrete table pipeline.

**Output**
- `data/company_product/canon/processed_data/camera/normalized.json`
- Each product includes `run_summary` counts:
  - mapped/unmapped/tables/documents
- Each product also includes:
  - `extraction` (raw_html_path, extraction errors, completeness)
  - `needs_pdf` + `needs_pdf_reasons`
- A PDF queue is generated for manual download:
  - `data/company_product/canon/processed_data/camera/pdf_queue.json`

#### Table pipeline (first implementation): Still Image \"File Size\" table → matrix_records

We convert the Canon HTML table labeled **"File Size"** (under "Recording System") into a matrix-shaped record:

- `normalized_key = still_image_file_size_table`
- `matrix_cells[]` dims: `format_group`, `quality`
- `numeric_value` stores file size in MB when the cell is a single numeric (e.g., `8.3`)
- `value_text` preserves the other table columns (`possible_shots`, `max_burst`) and the original file-size cell text

Note: some Canon rows express file size like `27.5 + 8.3`. For v1 we keep the full expression in `value_text.file_size_cell` and set `numeric_value` to the first numeric token (so we never lose information while keeping a usable numeric).

This produces a `matrix_records[]` entry in `normalized.json` and marks the original table record with `converted_to_matrix=true`. Later this will persist into `product_spec_matrix`.

**Run**
```bash
export DATABASE_URL="postgresql://postgres:postgres@127.0.0.1:54322/postgres"
python3 backend/scripts/run.py --stage normalize
```

### HTML inconsistency handling (Canon reality)

Canon’s shop pages are not consistent: some products may have **no `tech-spec-data` block** even though a PDF exists.

We handle this by:

- adding extraction `completeness` metrics (section/attribute counts) + `needs_pdf`
- propagating those fields into normalized output
- generating `pdf_queue.json` when `needs_pdf=true` and a PDF URL exists

This keeps the pipeline moving without blocking on PDF extraction implementation.

### Mapping iteration loop (how unmapped drops over time)

Mappings live in the DB table `spec_mapping`. The workflow is:
- run normalize
- inspect `unmapped`
- add context-aware mapping rules as migrations
- reset/apply migrations
- re-run normalize and re-check counts

**Migration we added for Canon camera label variants**
- `supabase/migrations/20251228002000_seed_spec_mapping_canon_camera.sql`

**Note on regex escaping**
- We normalize double-backslashes when compiling regex in Python so the same patterns work when seeded via SQL.

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

#### Product documents (PDF links) — store as rows, not strings

When the Canon site exposes links like **“View Full Technical Specs PDF”**, treat those as first-class assets.

- Extraction should capture the link URL (e.g. `context.pdf_url`) alongside the raw key/value pair.
- Persist discovered document URLs into a dedicated table:
  - `product_document`
    - `product_id` (optional FK, fill later)
    - `brand_slug`, `product_type`, `product_slug`
    - `document_kind` (e.g. `technical_specs_pdf`)
    - `url`, `source_url`, `status`, timestamps, `raw_metadata`

Suggested workflow:

- Run extraction
- Run importer `backend/scripts/import_documents_from_extractions.py` to upsert PDF URLs into `product_document`
- Download PDFs later (manual step), then update `product_document.status` to `downloaded` and set `local_path`

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

