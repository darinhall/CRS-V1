from dataclasses import dataclass
from typing import Any, Dict, List, Optional

import re

from bs4 import BeautifulSoup


@dataclass
class ParsedHtmlTable:
    headers: List[str]
    rows: List[List[str]]


def parse_html_table(table_html: str) -> ParsedHtmlTable:
    """
    Minimal deterministic HTML table parser.

    Later:
    - support multi-row headers
    - support row header columns
    - normalize whitespace
    """
    soup = BeautifulSoup(table_html or "", "html.parser")
    table = soup.find("table")
    if table is None:
        return ParsedHtmlTable(headers=[], rows=[])

    # naive: first row headers
    headers: List[str] = []
    first_tr = table.find("tr")
    if first_tr is not None:
        ths = first_tr.find_all(["th", "td"])
        headers = [th.get_text(" ", strip=True) for th in ths]

    rows: List[List[str]] = []
    for tr in table.find_all("tr")[1:]:
        tds = tr.find_all(["td", "th"])
        rows.append([td.get_text(" ", strip=True) for td in tds])

    return ParsedHtmlTable(headers=headers, rows=rows)


def infer_dims(headers: List[str]) -> Dict[str, Any]:
    """
    Stub: infer dimension schema from headers.

    Returns a JSON-serializable schema:
      {\"dims\": [...], \"value_fields\": [...]}
    """
    return {"dims": [], "value_fields": ["value_text"]}


def normalize_canon_still_file_size_table(table_html: str) -> Dict[str, Any]:
    """
    Canon \"File Size\" table (still images) → matrix cells.

    Table shape (observed):
    - first row headers include: Image Quality, File Size [Approx. MB], Possible Shots, Maximum Burst ...
    - first column is a row group like JPEG*2, HEIF*3, RAW, RAW+JPEG*2, RAW+HEIF*3 (often with rowspan)
    - second column is the quality / size variant (L, M, S1, S2, RAW, C-RAW, RAW + L, etc.)

    Output shape:
    - dims: [\"format_group\", \"quality\"]
    - cells[]: each row contains file_size_mb (numeric_value) plus extra metrics in value_text.

    Note: product_spec_matrix has only one numeric_value column. We store file_size_mb in numeric_value and
    pack the other columns into value_text (JSON-like string) for now. We can later split into separate
    matrix specs (possible_shots, max_burst) if desired.
    """
    soup = BeautifulSoup(table_html or "", "html.parser")
    table = soup.find("table")
    if table is None:
        return {"dims": ["format_group", "quality"], "value_fields": ["file_size_mb", "possible_shots", "max_burst"], "cells": []}

    rows = table.find_all("tr")
    if len(rows) < 2:
        return {"dims": ["format_group", "quality"], "value_fields": ["file_size_mb", "possible_shots", "max_burst"], "cells": []}

    current_group = None
    cells: List[Dict[str, Any]] = []

    for tr in rows[1:]:
        tds = tr.find_all("td")
        if not tds:
            continue

        # Some rows include group+quality+metrics; others omit group due to rowspan.
        # Heuristic: if first cell contains letters and not a short quality like L/M/S1..., treat as group.
        first = tds[0].get_text(" ", strip=True)
        if len(tds) >= 5:
            # group is present in this row
            current_group = first
            quality = tds[1].get_text(" ", strip=True)
            file_size = tds[2].get_text(" ", strip=True)
            possible_shots = tds[3].get_text(" ", strip=True)
            max_burst = tds[4].get_text(" ", strip=True)
        else:
            # group omitted (rowspan continuation)
            quality = tds[0].get_text(" ", strip=True)
            file_size = tds[1].get_text(" ", strip=True) if len(tds) > 1 else ""
            possible_shots = tds[2].get_text(" ", strip=True) if len(tds) > 2 else ""
            max_burst = tds[3].get_text(" ", strip=True) if len(tds) > 3 else ""

        group = (current_group or "").strip()
        if not group:
            # can't assign dims without group
            continue

        # Parse file size MB (first float in cell; supports \"27.5 + 8.3\" -> numeric_value = 27.5 + 8.3? keep None)
        numeric_value = None
        m = re.search(r"([0-9]+(?:\\.[0-9]+)?)", file_size or "")
        if m:
            try:
                numeric_value = float(m.group(1))
            except ValueError:
                numeric_value = None

        # Store extra metrics in value_text so we don't lose information
        value_text = {
            "file_size_cell": file_size,
            "possible_shots": possible_shots,
            "max_burst": max_burst,
        }

        cells.append(
            {
                "dims": {"format_group": group, "quality": quality},
                "numeric_value": numeric_value,
                "unit_used": "MB",
                "value_text": value_text,
                "extraction_confidence": 1.0,
            }
        )

    return {"dims": ["format_group", "quality"], "value_fields": ["numeric_value(MB)", "possible_shots", "max_burst"], "cells": cells}

