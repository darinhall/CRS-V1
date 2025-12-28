## Spec pipeline format (DB-first, UI-friendly, LLM-friendly)

This document is a **playbook** for how we ingest specs (website + PDFs), normalize them, and store them in Postgres/Supabase in a way that supports:

- **interactive UIs** (filters, compare, charts, accordions)
- **reliable scraping/normalization** (typed values + provenance)
- **LLM querying** (clean keys + structured text/JSON to retrieve)

It also records the **gotchas/issues** we hit while evolving the schema and local dev workflow.

---

## Core design goals

- **One canonical key per spec** (`spec_definition.normalized_key`)
- **One row per product/spec** (`product_spec` unique on `(product_id, spec_definition_id)`)
- **Typed values whenever possible** (numeric/range/boolean) to enable search, sorting, charts, and comparisons
- **Provenance preserved** (raw strings + optional structured JSON) so we can debug extraction and cite sources
- **Tabular specs** (PDF tables) handled as **structured child data**, not shoved into a single text blob

---

## Database taxonomy (normalized backbone)

### Tables (singular naming)

- **`brand`**: Canon, Sony, etc.
- **`product_category`**: Cameras, Lenses, etc. (with parent categories)
- **`product`**: a camera model (brand/category/model/name/slug + metadata)
- **`spec_section`**: UI/semantic grouping (General, Image Sensor, Display, Shutter, Storage, etc.)
- **`spec_definition`**: canonical spec key taxonomy (Effective Pixels, Lens Mount, etc.)
- **`product_spec`**: per-product values for each `spec_definition`

### Key idea: `spec_definition` is the canonical “key”

We do **not** store a denormalized `spec_key` on `product_spec`. The key is always:

- `spec_definition.normalized_key`  (canonical key)
- `spec_definition.display_name`    (human label)
- `spec_definition.unit`            (canonical/default unit)

`product_spec` stores the values and any source/unit differences:

- `spec_value` (cleaned display text)
- `raw_value` (verbatim extraction string, may be messy/not JSON)
- `raw_value_jsonb` (optional structured provenance/extraction artifacts)
- `numeric_value/min_value/max_value` (for filtering/graphs/ranges)
- `unit_used` (what the source actually used; may differ from canonical)
- `boolean_value`
- `extraction_confidence` (0–1)

### Why we removed denormalized fields from `product_spec`

We originally had `product_spec.spec_section` and `product_spec.spec_key` as TEXT. This was removed because it can drift:

- typos / casing differences
- renaming sections breaks historical rows
- conflicting “same meaning, different string” issues

Instead, section + key come from joins:

- `product_spec` → `spec_definition` → `spec_section`

---

## Handling units and normalization

### Canonical unit vs observed unit

- **`spec_definition.unit`**: what we want as the canonical unit (target for normalization)
- **`product_spec.unit_used`**: what the source used (oz, g, in, mm, stops, ISO, etc.)

**Do not hardcode `unit_used` just because a canonical unit exists.**

### Numeric normalization guidelines

- If the value is a scalar number, populate:
  - `numeric_value`
  - `unit_used` (if known)
  - `spec_value` (human-friendly string)

- If it’s a range, populate:
  - `min_value`, `max_value`
  - `unit_used`
  - `spec_value` (human-friendly range text)

- If it’s boolean-like:
  - `boolean_value`
  - `spec_value` (“Yes/No” + short detail)

### “Stops” as a unit

`unit_used = 'stops'` is valid for things like stabilization, exposure compensation, etc.

---

## Handling tabular specs (PDF tables, matrix-like specs)

Some specs are not “single value” — they’re tables/matrices (e.g. “Recording pixels — cropping & aspect ratios”).

### The pattern

1) Create a parent `spec_definition` for the table spec
   - `normalized_key` example: `still_image_recording_pixels`
   - `data_type` can be `'matrix'` (string taxonomy)

2) Insert a parent `product_spec` row for discoverability:
   - `spec_value`: “See matrix rows”
   - `raw_value`: human pointer (“PDF table: …”)
   - `raw_value_jsonb`: structured provenance (source, notes, dimension keys)

3) Store the actual table cells in a child table:
   - **`product_spec_matrix`**

### `product_spec_matrix` shape (generic “cell table”)

Each row is one “cell”:

- `product_id`
- `spec_definition_id` (points to the table spec key)
- `dims JSONB NOT NULL` (unbounded dimensions)
  - example:
    - `{"media_type":"JPEG/HEIF","image_size":"L","aspect_ratio":"3:2"}`

Value fields (small universal set):

- `numeric_value` (e.g., MP)
- `unit_used` (e.g., MP)
- `width_px`, `height_px` (for pixel dimension tables)
- `value_text` (e.g., “Not available”)

Metadata:

- `is_available` boolean
- `is_inexact_proportion` boolean (PDF shading marker)
- `notes` text
- `extraction_confidence`

**Why JSONB `dims`**:

- avoids “dim1..dim15” empty columns
- supports future tables with many axes (quality, crop, bit-depth, etc.)
- indexable with GIN if needed

---

## Views for UI-friendly shapes

We create views so the frontend doesn’t need to reshape raw rows.

Example view:

- `v_still_image_recording_pixels_grid`
  - one row per `(product_slug, media_type, image_size)`
  - `cells` JSON keyed by `aspect_ratio`
  - includes `{mp, width_px, height_px, availability flags, notes}`

This supports:

- accordion/table display
- compare view
- easy API payloads

---

## Seeding pattern (manual skeleton → scalable ingestion)

### Why seed at all

Seed entries establish a “clean skeleton” so:

- taxonomy exists (`spec_definition`, `spec_section`)
- UI can be built immediately
- later scraping can update/overwrite with confidence and provenance

### Seed conventions

- Use `ON CONFLICT DO NOTHING` on inserts for idempotency
- Use PL/pgSQL `DO $$ ... $$` blocks for “lookup IDs then insert rows”
- Avoid variable names that conflict with column names (see gotchas)

### Gotcha: ambiguous `product_id` variable

In PL/pgSQL blocks, a variable named `product_id` conflicted with the `product_id` column in `INSERT ... SELECT`.

Fix: prefix variables with `v_`:

- `v_product_id`, `v_cat_id`, etc.

---

## Migration + local dev workflow (Supabase CLI)

### Goal

Stop copy/pasting schema/seed into Supabase Cloud SQL editor and instead have:

- versioned migrations
- repeatable local reset
- predictable push to cloud

### What we set up

- `supabase/` directory via `supabase init`
- `supabase/migrations/*.sql` migration files
- `supabase/config.toml` configured to seed from `backend/db/seed.sql`

### Local run loop

- `supabase start` (requires Docker daemon)
- `supabase db reset` (rebuild schema + seed)
- use **Supabase Studio** at `http://localhost:54323`:
  - Table Editor: browse rows
  - SQL Editor: run queries and see results

### Gotcha: Docker daemon not running

`supabase start` failed with:

- “Cannot connect to the Docker daemon…”

Fix: start Docker Desktop or Colima.

### Gotcha: psql meta-commands in migrations/seeds

We initially tried to use:

- `\set ON_ERROR_STOP on`
- `\ir path/to/file.sql`

These are `psql` meta-commands and **not valid SQL** when Supabase executes migration files.

Fix:

- migrations must contain plain SQL
- seed paths in `supabase/config.toml` should point directly to an SQL file (no `\ir`)

### Best practice for future schema changes

Do not edit the init migration after it’s established. Instead:

- create new migrations for incremental schema changes
- reset locally to test:
  - `supabase db reset`
- push to hosted project:
  - `supabase link --project-ref <ref>`
  - `supabase db push`

---

## Extraction confidence guidelines

Use `extraction_confidence` to reflect how direct the value is:

- **1.0**: verbatim from an official spec table / clearly labeled field
- **0.9–0.95**: strong match but mild formatting normalization
- **0.7–0.85**: derived/inferred (e.g., “focal length multiplier 1.0x because full-frame”)
- **< 0.7**: uncertain; prefer leaving blank until confirmed

Never guess values if the source cannot be verified—store a TODO or omit the spec until verified.

---

## Why this structure supports “hands-on” UI + LLM queries

### UI (JS queries)

- filtering/sorting uses typed columns (`numeric_value`, `min/max`, booleans)
- grouping uses `spec_section`
- complex tables use `product_spec_matrix` + views

### LLM

LLMs benefit from:

- stable keys (`normalized_key`)
- clear display names (`display_name`)
- provenance (`raw_value`, `raw_value_jsonb`)
- pre-grouped views for retrieval (one query to fetch a structured payload)

---

## Suggested agent responsibilities (for later implementation)

### Discovery Agent

- finds product pages + PDFs
- outputs URLs + candidate sections

### Extraction Agent

- extracts raw key/value pairs
- extracts table specs into structured JSON (dims + cells)
- outputs `raw_value` (verbatim) and `raw_value_jsonb` (structured)

### Normalization Agent

- maps raw keys to `spec_definition.normalized_key`
- parses numeric/range/boolean
- sets `unit_used`
- sets `extraction_confidence`
- writes to `product_spec` and `product_spec_matrix`

---

## Agent output contract (what each stage must emit)

This contract is designed so you can swap implementations (Playwright scraper vs PDF parser vs LLM extractor)
without changing the downstream normalization + DB writer.

### Contract principles

- **Every extracted spec must be traceable** to a source: URL/PDF + location.
- Keep **both**:
  - verbatim text (`raw_value`) and
  - structured data (`raw_value_jsonb`, table cells)
- For tabular specs: emit both
  - parent spec (a single object keyed by `normalized_key`), and
  - `matrix_cells[]` rows (one per “cell”).

### 1) Discovery output (URL inventory)

```json
{
  "brand": "canon",
  "category_slug": "mirrorless-cameras",
  "listing_url": "https://www.usa.canon.com/shop/cameras/mirrorless-cameras",
  "discovered": [
    {
      "product_url": "https://www.usa.canon.com/shop/p/eos-r6-mark-iii",
      "product_slug_hint": "eos-r6-mark-iii",
      "source_type": "web",
      "confidence": 0.95
    }
  ],
  "run_metadata": {
    "started_at": "2025-12-23T00:00:00Z",
    "finished_at": "2025-12-23T00:01:00Z"
  }
}
```

### 2) Extraction output (raw manufacturer keys grouped by manufacturer sections)

We standardize on a **list-of-sections** shape because it supports:
- per-attribute `context` (PDF URLs, table HTML, etc.)
- keeping table values structured without flattening

```json
{
  "source": {
    "type": "web",
    "url": "https://www.usa.canon.com/shop/p/eos-r6-mark-iii",
    "retrieved_at": "2025-12-23T00:00:00Z"
  },
  "product": {
    "brand_slug": "canon",
    "category_slug": "mirrorless-cameras",
    "model": "EOS R6 Mark III",
    "full_name": "Canon EOS R6 Mark III",
    "slug_hint": "eos-r6-mark-iii"
  },
  "manufacturer_sections": [
    {
      "section_name": "Image Sensor",
      "attributes": [
        {"raw_key": "Effective Pixels", "raw_value": "Approx. 32.5 million pixels"},
        {"raw_key": "Sensor Type", "raw_value": "Full-frame CMOS"}
      ]
    },
    {
      "section_name": "Connectivity",
      "attributes": [
        {"raw_key": "Transmission Method", "raw_value": "Wi-Fi (IEEE 802.11ac), Bluetooth 5.1"}
      ]
    }
  ],
  "raw_html_ref": {
    "stored": false,
    "note": "If stored, provide storage URI + hash for reproducibility"
  }
}
```

### 3) Normalization output (DB-ready, typed, canonical)

Normalization emits a list of `spec_records[]`. Each record maps to exactly one `spec_definition.normalized_key`.

Policy:
- **`raw_value` is preserved verbatim** for provenance/debugging.
- **`spec_value` is cleaned deterministically** (whitespace + bullet cleanup) for UI display.
- PDF links are **documents**, not specs: they are routed to `product_document` and surfaced as `documents[]` in normalized output.
- HTML tables may be represented as `table_records[]` initially.
  - First implemented conversion: Canon still-image **\"File Size\"** HTML table → `matrix_records[]` + `matrix_cells[]`.

```json
{
  "product": {
    "brand_slug": "canon",
    "category_slug": "mirrorless-cameras",
    "slug": "eos-r6-mark-iii"
  },
  "spec_records": [
    {
      "normalized_key": "effective_pixels",
      "spec_value": "Approx. 32.5 MP",
      "raw_value": "Approx. 32.5 million pixels",
      "numeric_value": 32.5,
      "unit_used": "MP",
      "extraction_confidence": 0.95,
      "source": {
        "type": "web",
        "url": "https://www.usa.canon.com/shop/p/eos-r6-mark-iii",
        "section": "Image Sensor",
        "label": "Effective Pixels"
      }
    },
    {
      "normalized_key": "gps",
      "spec_value": "No (use smartphone GPS via Canon Camera Connect)",
      "raw_value": "No built-in GPS; geotag via Canon Camera Connect",
      "boolean_value": false,
      "extraction_confidence": 0.9,
      "source": {
        "type": "web",
        "url": "https://www.usa.canon.com/shop/p/eos-r6-mark-iii",
        "section": "Connectivity",
        "label": "GPS"
      }
    }
  ],
  "documents": [
    {
      "document_kind": "technical_specs_pdf",
      "url": "https://www.usa.canon.com/.../some-tech-specs.pdf",
      "source": {
        "type": "web",
        "url": "https://www.usa.canon.com/shop/p/eos-r6-mark-iii",
        "section": "View Full Technical Specs PDF",
        "label": "Techs. Specs. Detailed PDF"
      }
    }
  ],
  "matrix_records": [
    {
      "normalized_key": "still_image_recording_pixels",
      "spec_value": "See product_spec_matrix",
      "raw_value": "PDF table: Recording pixels — cropping & aspect ratios",
      "raw_value_jsonb": {
        "source": "canon_pdf",
        "page": 1,
        "notes": ["rounded values", "shaded = inexact proportion"],
        "dims": ["media_type","image_size","aspect_ratio"],
        "value_fields": ["mp","width_px","height_px","is_available","is_inexact"]
      },
      "matrix_cells": [
        {
          "dims": {"media_type":"JPEG/HEIF","image_size":"L","aspect_ratio":"3:2"},
          "numeric_value": 32.3,
          "unit_used": "MP",
          "width_px": 6960,
          "height_px": 4640,
          "is_available": true,
          "is_inexact_proportion": false,
          "notes": null,
          "extraction_confidence": 1.0
        }
      ]
    }
  ]
}
```

### 4) Validation output (quality + what to fix)

```json
{
  "valid": true,
  "quality_score": 0.92,
  "errors": [],
  "warnings": [
    {
      "normalized_key": "max_resolution",
      "issue": "Value seems to describe video Open Gate, not max still resolution",
      "confidence": 0.7
    }
  ],
  "flagged_for_review": [
    {"normalized_key":"focal_length_multiplier","reason":"inferred full-frame crop factor"}
  ]
}
```

### 5) Persistence output (what was written to DB)

```json
{
  "product_slug": "eos-r6-mark-iii",
  "upserts": {
    "spec_definitions_created": 3,
    "product_specs_upserted": 27,
    "product_spec_matrix_rows_upserted": 25
  },
  "conflicts": {
    "product_specs_ignored_due_to_conflict": 0
  }
}
```

---

## 5-agent “family” breakdown (per product type)

Your repo currently has these components:

- **`DiscoveryAgent`** (`backend/src/agents/discovery_agent.py`): Playwright discovery of product URLs
- **`ExtractionAgent`** (`backend/src/agents/extraction_agent.py`): Playwright extraction of Canon spec groups (with TODO for table extraction)
- **`normalization_agent.py`**: a multi-agent orchestration example (Extractor → Mapper → Validator → Enricher + Orchestrator)
- **`SpecMapperService`** (`backend/src/services/spec_mapper.py`): regex-based mapping service (note: table names must match your singular schema)

We standardize each product type into a 5-part “family”:

1) **Discovery**: find product URLs and supporting artifacts (PDF/manuals)
2) **Extraction**: pull raw manufacturer keys/values (and raw table structures)
3) **Mapping/Normalization**: map raw keys → `normalized_key`, parse typed values, attach provenance, produce DB-ready records
4) **Validation/QA**: schema + semantic validation, flag anomalies, assign quality score
5) **Persistence**: upsert to DB (including matrix cells), log what changed

Optional add-on (used when needed):

- **Enrichment**: fill missing specs from trusted sources *only if you accept non-manufacturer sources*; keep provenance and lower confidence.

### How this ties to your schema

- **Discovery** feeds `product.source_url` and/or URL lists.
- **Extraction** feeds raw JSON grouped by manufacturer section names.
- **Normalization** produces:
  - `spec_definition` (create missing keys)
  - `product_spec` rows
  - `product_spec_matrix` rows for table specs
- **Validation** decides what is safe to write vs hold for review.
- **Persistence** performs DB upserts and returns a summary (counts/conflicts).

---

## Next-step LangChain plan (concrete)

Goal: replace the ad-hoc “LLM returns prose” behavior with deterministic tool-driven extraction that emits the contract above.

### Phase 1: Web extraction (Canon shop pages)

- Wrap `discover_brand_products` as a LangChain tool (already done via `@tool`).
- Wrap `extract_product_specs` as a LangChain tool (already done via `@tool`).
- Extend `ExtractionAgent._parse_canon_specs` to:
  - detect `<table>` blocks and extract them into structured JSON (rows/cols/cells)
  - emit a `tables[]` section in extraction output (not just `"[Table Data]"`)

### Phase 2: PDF extraction

- Add a “PDF table extractor” tool:
  - choose a deterministic library (e.g. `camelot`, `tabula`, or `pdfplumber`) for table extraction
  - fallback to OCR for scanned PDFs
- Emit `matrix_records[]` using the contract above.

### Phase 3: Mapping/Normalization

- Prefer DB-driven mapping rules (`spec_mapping`) for stability.
- Use an LLM as a **fallback only** when no mapping rule exists:
  - output: proposed mapping + confidence + rationale
  - do not auto-write low-confidence mappings

### Phase 4: DB writer

- Upsert `product` row first (by `slug`)
- Create/lookup `spec_definition` by `normalized_key`
- Upsert `product_spec` by `(product_id, spec_definition_id)`
- Upsert matrix cells by `(product_id, spec_definition_id, dims)`

### Phase 5: QA loops

- Maintain a “review queue” for:
  - inferred values
  - unit conflicts
  - ambiguous keys
  - missing required “tier 1” specs

---

## Known pitfalls & how to avoid them (summary)

- **PL/pgSQL variable conflicts** → prefix variables (`v_product_id`)
- **denormalized keys/sections** → derive from joins, not stored text
- **table specs in one text field** → use `product_spec_matrix` + views
- **psql meta-commands in migrations** → migrations must be pure SQL
- **local Supabase requires Docker** → start Docker daemon first
- **avoid “edit init migration forever”** → add new migrations over time

---

## Future extensions (when needed)

- add a normalized “list item” table for filterable lists (optional)
- materialized views for performance (only when needed)
- embeddings/text-search “product doc” view for LLM retrieval (optional)

## General Thoughts
- using `discovery_agent.py` and `extraction_agent.py` as core classes for the extraction process
- having each folder separate by product type (camera, lens, tripod, bags & cases, drones & aerial, etc.)
- in each folder, there will be the following: init.py, product type specific agents (tailored queries or workflow for specific expected attribute keys and values), validators used to both secure data validity and agentically enhance the data if it is not found, and a file for json mappings 
- agents will also have a config file that allows 