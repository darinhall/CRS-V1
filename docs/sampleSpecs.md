## Sample spec payloads (current pipeline output)

This file is a **copy/paste reference** for what we currently emit in:

- `data/company_product/canon/processed_data/camera/normalized.json`

It’s intentionally **trimmed** (fewer records + truncated table HTML) so it stays readable.

### Notes

- `spec_records[]` are “simple” specs (persisted into `product_spec`).
- `matrix_records[]` are table/matrix specs (persisted into `product_spec_matrix` plus a parent `product_spec` row).
- `table_records[]` are the original extracted tables (some are converted to matrices; those have `converted_to_matrix: true`).
- `spec_definition_id` UUIDs may differ between databases; persistence resolves the live FK by `normalized_key` at write time.

### Example: one Canon camera item (excerpt)

```json
{
  "brand": "canon",
  "product_type": "camera",
  "generated_at": "2025-12-28T04:37:04.992950+00:00",
  "items": [
    {
      "product": {
        "brand_slug": "canon",
        "category_slug": "mirrorless-cameras",
        "product_type": "camera",
        "slug": "eos-r1",
        "manufacturer_url": "https://www.usa.canon.com/shop/p/eos-r1"
      },
      "run_summary": {
        "mapped_count": 24,
        "unmapped_count": 79,
        "tables_count": 15,
        "documents_count": 1
      },
      "needs_pdf": false,
      "needs_pdf_reasons": [],
      "extraction": {
        "raw_html_path": "data/company_product/canon/raw_html/eos-r1.html",
        "completeness": {
          "total_sections": 28,
          "total_attributes": 119,
          "tables_found": 15,
          "pdf_urls_found": 1,
          "meets_min_sections": true,
          "meets_min_attributes": true,
          "needs_pdf": false,
          "score": 1.0
        },
        "errors": []
      },
      "spec_records": [
        {
          "spec_definition_id": "76dd78ba-0077-4901-ac01-c4886e185e94",
          "normalized_key": "body_type",
          "spec_value": "Digital interchangeable lens, mirrorless camera",
          "raw_value": "Digital interchangeable lens, mirrorless camera",
          "numeric_value": null,
          "boolean_value": null,
          "unit_used": null,
          "extraction_confidence": 0.9,
          "source": {
            "type": "web",
            "url": "https://www.usa.canon.com/shop/p/eos-r1",
            "section": "Type",
            "label": "Type"
          }
        },
        {
          "spec_definition_id": "4044e248-b585-4bee-bb18-5e342fe146c3",
          "normalized_key": "effective_pixels",
          "spec_value": "Approx. 24.2 megapixels",
          "raw_value": "Approx. 24.2 megapixels",
          "numeric_value": null,
          "boolean_value": null,
          "unit_used": "MP",
          "extraction_confidence": 0.9,
          "source": {
            "type": "web",
            "url": "https://www.usa.canon.com/shop/p/eos-r1",
            "section": "Image Sensor",
            "label": "Effective Pixels"
          }
        }
      ],
      "matrix_records": [
        {
          "normalized_key": "still_image_file_size_table",
          "spec_value": "See product_spec_matrix",
          "raw_value": "HTML table: File Size (approx. MB) / possible shots / max burst",
          "raw_value_jsonb": {
            "source": {
              "type": "web",
              "url": "https://www.usa.canon.com/shop/p/eos-r1",
              "section": "Recording System",
              "label": "File Size"
            },
            "dims": [
              "format_group",
              "quality"
            ],
            "value_fields": [
              "numeric_value(MB)",
              "possible_shots",
              "max_burst"
            ]
          },
          "matrix_cells": [
            {
              "dims": {
                "format_group": "JPEG*2",
                "quality": "L"
              },
              "numeric_value": 8.0,
              "unit_used": "MB",
              "value_text": {
                "file_size_cell": "8.3",
                "possible_shots": "37930",
                "max_burst": "1000 or more"
              },
              "extraction_confidence": 1.0
            }
          ]
        }
      ],
      "table_records": [
        {
          "section": "Recording System",
          "label": "File Size",
          "raw_value": "[table]",
          "raw_value_jsonb": {
            "source": {
              "type": "web",
              "url": "https://www.usa.canon.com/shop/p/eos-r1",
              "section": "Recording System",
              "label": "File Size"
            },
            "table_html": "<table>... truncated for docs ...</table>",
            "text_fallback": "Image Quality File Size [Approx. MB] Possible Shots [Approx.] ... (truncated)"
          },
          "converted_to_matrix": true
        }
      ],
      "documents": [
        {
          "document_kind": "technical_specs_pdf",
          "url": "https://s7d1.scene7.com/is/content/canon/EOS-R1-final-spec-sheetpdf",
          "source": {
            "type": "web",
            "url": "https://www.usa.canon.com/shop/p/eos-r1",
            "section": "View Full Technical Specs PDF",
            "label": "Techs. Specs. Detailed PDF"
          }
        }
      ]
    }
  ]
}
```


