import json
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

import psycopg2

from agents.spec_pipeline.core.extraction import _normalize_url
from agents.spec_pipeline.core.text_normalizer import clean_text_for_spec_value
from agents.spec_pipeline.core.table_normalizer import normalize_canon_still_file_size_table
from services.spec_mapper import SpecMapperService


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


@dataclass
class NormalizationConfig:
    brand_slug: str
    product_type: str
    category_slug: Optional[str] = None
    output_path: str = "data/company_product/_normalized/normalized.json"


def normalize_extractions(
    config: NormalizationConfig,
    extractions_json_path: str,
    db_url: str,
) -> Dict[str, Any]:
    payload = json.loads(Path(extractions_json_path).read_text(encoding="utf-8"))
    items = payload.get("items", [])

    conn = psycopg2.connect(db_url)
    try:
        mapper = SpecMapperService(conn)
        normalized_items: List[Dict[str, Any]] = []
        pdf_queue: List[Dict[str, Any]] = []

        for item in items:
            product_slug = item.get("product_slug")
            product_url = _normalize_url(item.get("product_url", ""))
            raw_html_path = item.get("raw_html_path")
            extraction_errors = item.get("errors", []) or []
            extraction_completeness = item.get("completeness", {}) or {}

            spec_records: List[Dict[str, Any]] = []
            unmapped: List[Dict[str, Any]] = []
            table_records: List[Dict[str, Any]] = []
            documents: List[Dict[str, Any]] = []
            matrix_records: List[Dict[str, Any]] = []

            for section in item.get("manufacturer_sections", []) or []:
                section_name = section.get("section_name", "") or ""
                for attr in section.get("attributes", []) or []:
                    raw_key = attr.get("raw_key", "") or ""
                    raw_value = attr.get("raw_value", "") or ""
                    ctx = attr.get("context") or {}

                    # Document handling: PDF links are assets, not specs
                    if ctx.get("pdf_url"):
                        documents.append(
                            {
                                "document_kind": "technical_specs_pdf",
                                "url": ctx.get("pdf_url"),
                                "source": {
                                    "type": "web",
                                    "url": product_url,
                                    "section": section_name,
                                    "label": raw_key,
                                },
                            }
                        )
                        continue

                    # Table handling: defer to later matrix normalizer
                    if raw_value == "[table]":
                        table_rec = {
                            "section": section_name,
                            "label": raw_key,
                            "raw_value": raw_value,
                            "raw_value_jsonb": {
                                "source": {"type": "web", "url": product_url, "section": section_name, "label": raw_key},
                                "table_html": ctx.get("table_html"),
                                "text_fallback": ctx.get("text_fallback"),
                            },
                        }

                        # Attempt a first concrete table→matrix conversion: Canon still image \"File Size\" table.
                        mapped_table = mapper.map_spec(raw_key=raw_key, raw_context=section_name, raw_value=raw_value)
                        if mapped_table and (mapper.definitions.get(mapped_table["spec_definition_id"], {}).get("normalized_key") == "still_image_file_size_table"):
                            table_html = (ctx.get("table_html") or "")
                            normalized = normalize_canon_still_file_size_table(table_html)
                            matrix_records.append(
                                {
                                    "normalized_key": "still_image_file_size_table",
                                    "spec_value": "See product_spec_matrix",
                                    "raw_value": "HTML table: File Size (approx. MB) / possible shots / max burst",
                                    "raw_value_jsonb": {
                                        "source": {"type": "web", "url": product_url, "section": section_name, "label": raw_key},
                                        "dims": normalized.get("dims"),
                                        "value_fields": normalized.get("value_fields"),
                                    },
                                    "matrix_cells": normalized.get("cells", []),
                                }
                            )
                            table_rec["converted_to_matrix"] = True
                        else:
                            table_rec["converted_to_matrix"] = False

                        table_records.append(
                            {
                                **table_rec
                            }
                        )
                        continue

                    mapped = mapper.map_spec(raw_key=raw_key, raw_context=section_name, raw_value=raw_value)
                    if not mapped:
                        unmapped.append(
                            {
                                "section": section_name,
                                "label": raw_key,
                                "raw_value": raw_value,
                            }
                        )
                        continue

                    def_id = mapped["spec_definition_id"]
                    definition = mapper.definitions.get(def_id, {})

                    spec_records.append(
                        {
                            "spec_definition_id": def_id,
                            "normalized_key": definition.get("normalized_key"),
                            # Preserve raw_value; clean spec_value for UI
                            "spec_value": clean_text_for_spec_value(mapped.get("value_text") or raw_value),
                            "raw_value": raw_value,
                            "numeric_value": mapped.get("numeric_value"),
                            "boolean_value": mapped.get("boolean_value"),
                            "unit_used": mapped.get("unit_used"),
                            "extraction_confidence": 0.9,
                            "source": {
                                "type": "web",
                                "url": product_url,
                                "section": section_name,
                                "label": raw_key,
                            },
                        }
                    )

            normalized_items.append(
                {
                    "product": {
                        "brand_slug": config.brand_slug,
                        "category_slug": config.category_slug,
                        "product_type": config.product_type,
                        "slug": product_slug,
                        "manufacturer_url": product_url,
                    },
                    "extraction": {
                        "raw_html_path": raw_html_path,
                        "errors": extraction_errors,
                        "completeness": extraction_completeness,
                    },
                    "spec_records": spec_records,
                    "table_records": table_records,
                    "matrix_records": matrix_records,
                    "documents": documents,
                    "unmapped": unmapped,
                    "run_summary": {
                        "mapped_count": len(spec_records),
                        "unmapped_count": len(unmapped),
                        "tables_count": len(table_records),
                        "documents_count": len(documents),
                    },
                }
            )

            # HTML inconsistency handling: decide if we need PDFs for this product.
            needs_pdf_reasons: List[str] = []
            needs_pdf = False
            if extraction_errors:
                needs_pdf = True
                needs_pdf_reasons.append("extraction_errors")
            if extraction_completeness.get("needs_pdf") is True:
                needs_pdf = True
                needs_pdf_reasons.append("low_completeness")

            # If Canon HTML has no sections but we did find a PDF link, treat as needs_pdf.
            if len(spec_records) == 0 and len(unmapped) == 0 and len(documents) > 0:
                needs_pdf = True
                needs_pdf_reasons.append("no_html_specs")

            # Add needs_pdf + reasons to the last appended item (same product)
            normalized_items[-1]["needs_pdf"] = needs_pdf
            normalized_items[-1]["needs_pdf_reasons"] = needs_pdf_reasons

            if needs_pdf:
                for doc in documents:
                    if doc.get("document_kind") == "technical_specs_pdf" and doc.get("url"):
                        pdf_queue.append(
                            {
                                "brand": config.brand_slug,
                                "product_type": config.product_type,
                                "product_slug": product_slug,
                                "product_url": product_url,
                                "pdf_url": doc["url"],
                                "pdf_kind": "technical_specs_pdf",
                                "reason": ";".join(needs_pdf_reasons) or "needs_pdf",
                                "status": "needs_download",
                            }
                        )

        return {
            "brand": config.brand_slug,
            "product_type": config.product_type,
            "generated_at": _utc_now_iso(),
            "source_extractions_path": extractions_json_path,
            "items": normalized_items,
            "pdf_queue": pdf_queue,
        }
    finally:
        conn.close()

