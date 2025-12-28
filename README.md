# CRS-V1 / Altoscope

Altoscope is a comprehensive platform designed to empower visual creators by simplifying the research, discovery, and acquisition of professional camera equipment. By providing the industry's most robust and user-friendly database of gear specifications, Altoscope enables photographers and videographers to make informed decisions with unparalleled efficiency. Through seamlessly connecting this knowledge hub with rental houses, camera stores, and other various companies, Altoscope serves as a unified ecosystem for all visual media enthusiasts. The mission is to streamline the entire creative workflow, ensuring that every project or idea, from concept to completion, is supported by the right gear.

## Current progress (what works today)

- **Normalized Postgres/Supabase schema** for gear specs:
  - `brand`, `product_category`, `product`, `spec_section`, `spec_definition`, `spec_mapping`, `product_spec`
  - matrix/table specs in `product_spec_matrix` (`dims` is JSONB)
  - PDFs tracked in `product_document` (URLs stored; download/parse later)
- **End-to-end ingestion pipeline (Canon mirrorless cameras)**:
  - discovery → extraction (cache-first) → normalization (DB mapping + text cleanup) → persistence (DB upserts)
  - currently ingests **15 Canon mirrorless cameras** from `https://www.usa.canon.com/shop/cameras/mirrorless-cameras`
- **Table → matrix conversions implemented** (persisted into `product_spec_matrix`):
  - `still_image_file_size_table`
  - `playback_display_format_table`
  - `wifi_security_table`
- **UI-friendly SQL views** exist to support frontend payloads and grids (see Supabase migrations).

## Local dev workflow (high level)

- Start local Supabase + Studio:
  - `supabase start` (requires Docker)
  - Studio runs at `http://127.0.0.1:54323`
- Apply migrations locally:
  - `supabase db push --local`
- Run the pipeline (Canon defaults):
  - `python3 backend/scripts/run.py --stage discovery`
  - `python3 backend/scripts/run.py --stage extraction`
  - `DATABASE_URL="postgresql://postgres:postgres@127.0.0.1:54322/postgres" python3 backend/scripts/run.py --stage normalize`
  - `DATABASE_URL="postgresql://postgres:postgres@127.0.0.1:54322/postgres" python3 backend/scripts/run.py --stage persist`

## Next steps

- **Mapping coverage sprint**: reduce `unmapped[]` by adding `spec_mapping` rules as migrations.
- **More table→matrix converters** for high-value Canon tables, then expand brand coverage.
- **PDF download + parsing** (later): store URLs now, parse deterministically later.
