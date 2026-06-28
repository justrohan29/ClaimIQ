import json
import re
from difflib import SequenceMatcher
from datetime import datetime

import pandas as pd
from openai import OpenAI


# ==========================
# CONFIG
# ==========================

MD_FILE = "docling_output.md"
XLS_FILE = "PQ205.xls"
FUZZY_THRESHOLD = 0.85

client = OpenAI(
    api_key="sk-f66803b96c6c417d8df9a0b0db4ac1ae",
    base_url="https://api.deepseek.com"
)


# ==========================
# GENERIC MARKDOWN PARSER
# ==========================

def parse_markdown(path):
    """
    Generic parser for Docling markdown output.
    Auto-detects key-value pairs and tables — no hardcoded field names.

    Returns:
        {
            "kv_pairs": {"key": "value", ...},
            "tables": [{"headers": [...], "rows": [{...}, ...]}, ...]
        }
    """
    with open(path, "r", encoding="utf-8") as f:
        content = f.read()

    lines = content.splitlines()
    stripped = [l.strip() for l in lines]

    result = {"kv_pairs": {}, "tables": []}

    # ---- Extract key-value pairs ----
    # Matches lines containing : or ： with a key before and optional value after
    i = 0
    while i < len(stripped):
        line = stripped[i]

        # Skip empty, table, and comment lines
        if not line or line.startswith("|") or line.startswith("<!--"):
            i += 1
            continue

        colon_match = re.match(r'^(.+?)\s*[：:]\s*(.*)', line)
        if colon_match:
            key = colon_match.group(1).strip()
            value = colon_match.group(2).strip()

            if not value:
                # Value might be on the next non-empty line
                j = i + 1
                while j < len(stripped) and not stripped[j]:
                    j += 1
                if j < len(stripped):
                    next_line = stripped[j]
                    # Don't grab tables, comments, or other KV pairs as values
                    if (not next_line.startswith("|")
                            and not next_line.startswith("<!--")
                            and not re.match(r'^.+?[：:]', next_line)):
                        value = next_line

            # Sanity: keys shouldn't be very long (avoid capturing paragraphs)
            if key and len(key) < 80:
                result["kv_pairs"][key] = value

        i += 1

    # ---- Extract markdown tables ----
    raw_tables = []
    current_table = []

    for line in stripped:
        if line.startswith("|") and "|" in line[1:]:
            # Skip separator rows (|---|---|)
            if re.match(r'^\|[\s\-|:]+\|$', line):
                continue
            cells = [c.strip() for c in line.split("|")]
            cells = cells[1:-1]  # Remove empty first/last from | delimiters
            if cells:
                current_table.append(cells)
        else:
            if current_table:
                raw_tables.append(current_table)
                current_table = []

    if current_table:
        raw_tables.append(current_table)

    for raw in raw_tables:
        # 2-column tables → treat as KV pairs (summary-style tables)
        if all(len(row) == 2 for row in raw):
            for row in raw:
                if row[0].strip():
                    result["kv_pairs"][row[0].strip()] = row[1].strip()
            continue

        if len(raw) < 2:
            continue

        headers = raw[0]

        # Detect bilingual sub-header (second row with no numbers)
        data_start = 1
        if len(raw) > 2 and len(raw[1]) == len(headers):
            has_numbers = any(re.search(r'\d', c) for c in raw[1] if c)
            if not has_numbers:
                data_start = 2

        rows = []
        for ri in range(data_start, len(raw)):
            row_data = {}
            for ci, header in enumerate(headers):
                row_data[header] = raw[ri][ci] if ci < len(raw[ri]) else ""
            rows.append(row_data)

        result["tables"].append({"headers": headers, "rows": rows})

    # Merge consecutive tables with matching headers (handles multi-page PDF splits)
    merged_tables = []
    
    def headers_match(h1, h2, threshold=0.8):
        if len(h1) != len(h2):
            return False
        matches = 0
        for a, b in zip(h1, h2):
            a_norm = a.lower().replace(" ", "").strip()
            b_norm = b.lower().replace(" ", "").strip()
            if a_norm == b_norm or SequenceMatcher(None, a_norm, b_norm).ratio() >= threshold:
                matches += 1
        return (matches / len(h1)) >= 0.8

    for table in result["tables"]:
        if merged_tables and headers_match(merged_tables[-1]["headers"], table["headers"]):
            # Create mapping from this table's headers to previous table's headers
            h_prev = merged_tables[-1]["headers"]
            col_map = {}
            for col2 in table["headers"]:
                best_match = col2
                best_ratio = 0
                for col1 in h_prev:
                    ratio = SequenceMatcher(None, col2.lower().strip(), col1.lower().strip()).ratio()
                    if ratio > best_ratio:
                        best_match = col1
                        best_ratio = ratio
                col_map[col2] = best_match if best_ratio >= 0.8 else col2
            
            # Append rows with mapped keys
            for row in table["rows"]:
                new_row = {col_map.get(k, k): v for k, v in row.items()}
                merged_tables[-1]["rows"].append(new_row)
        else:
            merged_tables.append(table)
            
    result["tables"] = merged_tables

    return result


# ==========================
# GENERIC EXCEL PARSER
# ==========================

def _to_str(val):
    """Convert any cell value to a clean string."""
    if isinstance(val, (datetime, pd.Timestamp)):
        return val.strftime("%Y-%m-%d %H:%M:%S")
    if isinstance(val, float):
        if val == int(val) and abs(val) < 1e15:
            return str(int(val))
        return f"{val:.10g}"
    return str(val).strip()


def parse_excel(path):
    """
    Generic parser for Excel spotplans.
    Auto-detects metadata KV pairs, data tables, and summary sections.
    Works with any template layout.

    Returns:
        {
            "sheet_name": {
                "kv_pairs": {"key": "value", ...},
                "tables": [{"headers": [...], "rows": [{...}, ...]}, ...]
            }
        }
    """
    all_sheets = pd.read_excel(path, sheet_name=None, header=None)
    result = {}

    for sheet_name, df in all_sheets.items():
        sheet = {"kv_pairs": {}, "tables": []}

        # Analyze each row: list of (col_index, value) for non-empty cells
        row_infos = []
        for idx in range(df.shape[0]):
            cells = []
            for col in range(df.shape[1]):
                val = df.iloc[idx, col]
                if pd.notna(val) and str(val).strip():
                    cells.append((col, val))
            row_infos.append(cells)

        # Process rows: classify as KV pairs or table regions
        table_buffer = []  # row indices of consecutive table-like rows

        i = 0
        while i < len(row_infos):
            cells = row_infos[i]
            n = len(cells)

            if n == 0:
                # Empty row — flush any table buffer
                if table_buffer:
                    _flush_table(table_buffer, row_infos, df, sheet)
                    table_buffer = []
                i += 1
                continue

            if n >= 4:
                # Many cells → table row
                table_buffer.append(i)
                i += 1
                continue

            # n is 1, 2, or 3
            if table_buffer:
                # We're inside a table region — check if this row belongs
                first_val = str(cells[0][1]).strip().lower()
                if first_val in ("subtotal", "total") or n >= 3:
                    # Aggregation row or wide enough — keep in table
                    table_buffer.append(i)
                    i += 1
                    continue
                else:
                    # End the table, process this row as KV
                    _flush_table(table_buffer, row_infos, df, sheet)
                    table_buffer = []

            # KV pair extraction
            if n == 2:
                key = _to_str(cells[0][1]).rstrip("：:").strip()
                val = _to_str(cells[1][1])
                if key and key.lower() != "nan":
                    sheet["kv_pairs"][key] = val
            elif n == 3:
                # 3 cells — use first non-empty as key, last as value
                key = _to_str(cells[0][1]).rstrip("：:").strip()
                if not key or key.lower() == "nan":
                    key = _to_str(cells[1][1]).rstrip("：:").strip()
                val = _to_str(cells[-1][1])
                if key and key.lower() != "nan":
                    sheet["kv_pairs"][key] = val
            # n == 1: standalone cell — skip

            i += 1

        # Flush remaining table buffer
        if table_buffer:
            _flush_table(table_buffer, row_infos, df, sheet)

        result[sheet_name] = sheet

    return result


def _flush_table(buffer, row_infos, df, sheet):
    """Build a table from buffered row indices and add to sheet data."""
    if not buffer:
        return

    # Find all columns used across these rows
    used_cols = set()
    for idx in buffer:
        for col, _ in row_infos[idx]:
            used_cols.add(col)
    used_cols = sorted(used_cols)

    if not used_cols:
        return

    # First row = headers
    header_idx = buffer[0]
    headers = []
    for col in used_cols:
        val = df.iloc[header_idx, col]
        headers.append(_to_str(val) if pd.notna(val) else f"Col{col}")

    # Detect bilingual sub-header (second row with no numbers)
    data_start = 1
    if len(buffer) > 2:
        second_vals = []
        for col in used_cols:
            val = df.iloc[buffer[1], col]
            second_vals.append(_to_str(val) if pd.notna(val) else "")
        has_nums = any(re.search(r'\d', v) for v in second_vals if v)
        if not has_nums:
            data_start = 2

    # Build data rows
    rows = []
    for bi in range(data_start, len(buffer)):
        idx = buffer[bi]
        row_data = {}
        for ci, col in enumerate(used_cols):
            if ci < len(headers):
                val = df.iloc[idx, col]
                row_data[headers[ci]] = _to_str(val) if pd.notna(val) else ""
        rows.append(row_data)

    if headers and rows:
        sheet["tables"].append({"headers": headers, "rows": rows})


# ==========================
# LLM ALIGNMENT
# ==========================

def align_with_llm(md_data, xls_data):
    """
    Use DeepSeek to align OCR fields with Excel fields.
    Sends ONLY field names and column headers (no actual data values)
    to keep the call small and focused.

    Returns:
        {
            "kv_mapping": {"ocr_key": "excel_key", ...},
            "column_mapping": {"ocr_col": "excel_col", ...},
            "unmatched_ocr": [...],
            "unmatched_excel": [...]
        }
    """
    # Collect OCR structure
    ocr_kv_keys = list(md_data["kv_pairs"].keys())
    ocr_table_headers = []
    for t in md_data["tables"]:
        ocr_table_headers.extend(t["headers"])

    # Collect Excel structure (all sheets)
    xls_kv_keys = []
    xls_table_headers = []
    for sheet_data in xls_data.values():
        xls_kv_keys.extend(sheet_data["kv_pairs"].keys())
        for t in sheet_data["tables"]:
            xls_table_headers.extend(t["headers"])

    # De-duplicate
    xls_kv_keys = list(dict.fromkeys(xls_kv_keys))
    xls_table_headers = list(dict.fromkeys(xls_table_headers))

    prompt = f"""You are mapping fields between two representations of the SAME document.
One was OCR-extracted from a PDF, the other is from an Excel file.
They represent the same spotplan but field names may differ due to OCR errors,
different languages (Chinese/English), spacing, or formatting differences.

OCR KEY-VALUE FIELD NAMES:
{json.dumps(ocr_kv_keys, ensure_ascii=False, indent=2)}

OCR TABLE COLUMN HEADERS:
{json.dumps(ocr_table_headers, ensure_ascii=False, indent=2)}

EXCEL KEY-VALUE FIELD NAMES:
{json.dumps(xls_kv_keys, ensure_ascii=False, indent=2)}

EXCEL TABLE COLUMN HEADERS:
{json.dumps(xls_table_headers, ensure_ascii=False, indent=2)}

Match each OCR field to its corresponding Excel field. Consider:
- Fields may be in different languages (Chinese/English) but mean the same thing
- OCR may have typos, merged words, or missing spaces
- Column headers may be slightly different but refer to the same data

Return ONLY valid JSON (no markdown fences, no explanation):
{{
  "kv_mapping": {{
    "ocr_kv_field": "matching_excel_kv_field"
  }},
  "column_mapping": {{
    "ocr_column": "matching_excel_column"
  }},
  "unmatched_ocr": ["ocr_fields_with_no_excel_match"],
  "unmatched_excel": ["excel_fields_with_no_ocr_match"]
}}"""

    print("  Calling DeepSeek for field alignment...")

    response = client.chat.completions.create(
        model="deepseek-chat",
        temperature=0,
        messages=[
            {
                "role": "system",
                "content": (
                    "You are a field mapping assistant. You match fields between "
                    "OCR and Excel representations of the same document. "
                    "Return ONLY valid JSON, no markdown."
                )
            },
            {
                "role": "user",
                "content": prompt
            }
        ]
    )

    content = response.choices[0].message.content.strip()

    # Strip markdown code fences if present
    if content.startswith("```"):
        content = re.sub(r'^```(?:json)?\s*', '', content)
        content = re.sub(r'\s*```$', '', content)

    try:
        alignment = json.loads(content)
    except json.JSONDecodeError:
        print("  WARNING: Could not parse LLM alignment response as JSON.")
        print(f"  Raw response (first 500 chars): {content[:500]}")
        # Fallback: try fuzzy name matching
        alignment = _fallback_alignment(
            ocr_kv_keys, xls_kv_keys,
            ocr_table_headers, xls_table_headers
        )

    return alignment


def _fallback_alignment(ocr_kv, xls_kv, ocr_cols, xls_cols):
    """
    Fallback alignment using fuzzy string matching if LLM fails.
    """
    def best_match(name, candidates, threshold=0.6):
        best, best_ratio = None, 0
        norm = name.lower().replace(" ", "")
        for c in candidates:
            ratio = SequenceMatcher(None, norm, c.lower().replace(" ", "")).ratio()
            if ratio > best_ratio:
                best, best_ratio = c, ratio
        return best if best_ratio >= threshold else None

    kv_mapping = {}
    used_xls = set()
    for ok in ocr_kv:
        match = best_match(ok, [k for k in xls_kv if k not in used_xls])
        if match:
            kv_mapping[ok] = match
            used_xls.add(match)

    col_mapping = {}
    used_xls_cols = set()
    for oc in ocr_cols:
        match = best_match(oc, [c for c in xls_cols if c not in used_xls_cols])
        if match:
            col_mapping[oc] = match
            used_xls_cols.add(match)

    return {
        "kv_mapping": kv_mapping,
        "column_mapping": col_mapping,
        "unmatched_ocr": [k for k in ocr_kv + ocr_cols
                          if k not in kv_mapping and k not in col_mapping],
        "unmatched_excel": [k for k in xls_kv + xls_cols
                            if k not in used_xls and k not in used_xls_cols],
    }


# ==========================
# VALUE NORMALIZATION
# ==========================

def normalize_value(val):
    """Normalize a value for comparison: strip currency, commas, whitespace."""
    if val is None:
        return ""

    s = str(val).strip()
    s = s.replace("￥", "").replace("¥", "").replace(",", "").replace(" ", "")

    # Normalize percentage: "25%" → "0.25"
    pct = re.match(r'^(\d+(?:\.\d+)?)%$', s)
    if pct:
        return str(float(pct.group(1)) / 100)

    return s


def try_as_number(val):
    """Try parsing a normalized value as float."""
    try:
        return float(val)
    except (ValueError, TypeError):
        return None


# ==========================
# DETERMINISTIC COMPARISON
# ==========================

def compare_values(field_name, ocr_val, excel_val):
    """
    Compare two values deterministically.
    Uses: exact match → numeric match (±0.01) → fuzzy string match.
    """
    result = {
        "field": field_name,
        "ocr_value": str(ocr_val) if ocr_val else "",
        "excel_value": str(excel_val) if excel_val else "",
    }

    norm_ocr = normalize_value(ocr_val)
    norm_excel = normalize_value(excel_val)

    # Both empty
    if not norm_ocr and not norm_excel:
        result.update(status="match", confidence=1.0, reason="Both empty")
        return result

    # One empty
    if not norm_ocr or not norm_excel:
        result.update(status="mismatch", confidence=0.0, reason="One value is missing")
        return result

    # Exact match after normalization
    if norm_ocr == norm_excel:
        result.update(status="match", confidence=1.0, reason="Exact match")
        return result

    # Numeric comparison
    num_ocr = try_as_number(norm_ocr)
    num_excel = try_as_number(norm_excel)

    if num_ocr is not None and num_excel is not None:
        if abs(num_ocr - num_excel) < 0.01:
            result.update(status="match", confidence=1.0,
                          reason="Numeric match (within tolerance)")
        else:
            diff = abs(num_ocr - num_excel)
            pct = (diff / max(abs(num_ocr), abs(num_excel), 1)) * 100
            result.update(
                status="mismatch",
                confidence=round(max(0, 1 - pct / 100), 3),
                reason=f"Numeric mismatch: diff={diff:.2f} ({pct:.1f}%)"
            )
        return result

    # Fuzzy string match
    ratio = SequenceMatcher(None, norm_ocr.lower(), norm_excel.lower()).ratio()

    if ratio >= FUZZY_THRESHOLD:
        result.update(status="partial_match", confidence=round(ratio, 3),
                      reason=f"Fuzzy match (similarity={ratio:.3f})")
    else:
        result.update(status="mismatch", confidence=round(ratio, 3),
                      reason=f"Different values (similarity={ratio:.3f})")

    return result


# ==========================
# COMPARISON ENGINE
# ==========================

def run_comparison(md_data, xls_data, alignment):
    """
    Compare OCR data against Excel data using the LLM-produced alignment.
    Returns a clean, compact list of discrepancies and unmatched items.
    """
    discrepancies = []
    matched_count = 0
    partial_count = 0
    mismatch_count = 0

    # Collect all Excel KV pairs across sheets
    all_xls_kv = {}
    for sheet_data in xls_data.values():
        for k, v in sheet_data["kv_pairs"].items():
            all_xls_kv[k] = v

    # ---- Compare KV pairs ----
    kv_mapping = alignment.get("kv_mapping", {})
    for ocr_key, xls_key in kv_mapping.items():
        if not xls_key or xls_key.lower() in ("unmatched", "none", "n/a"):
            continue

        ocr_val = md_data["kv_pairs"].get(ocr_key, "")
        xls_val = all_xls_kv.get(xls_key, "")

        cmp = compare_values(f"{ocr_key} ↔ {xls_key}", ocr_val, xls_val)
        if cmp["status"] != "match":
            discrepancies.append({
                "category": "Header Field",
                "field": f"{ocr_key} ↔ {xls_key}",
                "pdf_value": str(ocr_val) if ocr_val else "",
                "excel_value": str(xls_val) if xls_val else "",
                "status": cmp["status"],
                "reason": cmp["reason"]
            })
            if cmp["status"] == "mismatch":
                mismatch_count += 1
            else:
                partial_count += 1
        else:
            matched_count += 1

    # ---- Compare tables ----
    col_mapping = alignment.get("column_mapping", {})
    md_tables = md_data.get("tables", [])
    xls_tables = []
    for sheet_data in xls_data.values():
        xls_tables.extend(sheet_data.get("tables", []))

    for t_idx in range(max(len(md_tables), len(xls_tables))):
        md_table = md_tables[t_idx] if t_idx < len(md_tables) else None
        xls_table = xls_tables[t_idx] if t_idx < len(xls_tables) else None

        if md_table is None:
            discrepancies.append({
                "category": "Table Layout",
                "field": f"Table {t_idx + 1}",
                "pdf_value": "(MISSING)",
                "excel_value": "(PRESENT)",
                "status": "mismatch",
                "reason": f"Entire table {t_idx + 1} is missing in the PDF"
            })
            mismatch_count += 1
            continue

        if xls_table is None:
            discrepancies.append({
                "category": "Table Layout",
                "field": f"Table {t_idx + 1}",
                "pdf_value": "(PRESENT)",
                "excel_value": "(MISSING)",
                "status": "mismatch",
                "reason": f"Entire table {t_idx + 1} is missing in the Excel file"
            })
            mismatch_count += 1
            continue

        md_rows = md_table.get("rows", [])
        xls_rows = xls_table.get("rows", [])
        max_rows = max(len(md_rows), len(xls_rows))

        for r_idx in range(max_rows):
            if r_idx >= len(md_rows):
                row_val = xls_rows[r_idx]
                row_desc = ", ".join(f"{k}: {v}" for k, v in row_val.items() if v)
                discrepancies.append({
                    "category": "Table Row",
                    "field": f"Table {t_idx + 1}, Row {r_idx + 1}",
                    "pdf_value": "(MISSING ROW)",
                    "excel_value": row_desc,
                    "status": "mismatch",
                    "reason": "Row exists in Excel but was not found in PDF"
                })
                mismatch_count += 1
                continue

            if r_idx >= len(xls_rows):
                row_val = md_rows[r_idx]
                row_desc = ", ".join(f"{k}: {v}" for k, v in row_val.items() if v)
                discrepancies.append({
                    "category": "Table Row",
                    "field": f"Table {t_idx + 1}, Row {r_idx + 1}",
                    "pdf_value": row_desc,
                    "excel_value": "(MISSING ROW)",
                    "status": "mismatch",
                    "reason": "Row exists in PDF but was not found in Excel"
                })
                mismatch_count += 1
                continue

            # Compare each mapped column
            for ocr_col, xls_col in col_mapping.items():
                ocr_val = md_rows[r_idx].get(ocr_col, "")
                xls_val = xls_rows[r_idx].get(xls_col, "")

                cmp = compare_values(f"Row {r_idx + 1}: {ocr_col} ↔ {xls_col}", ocr_val, xls_val)
                if cmp["status"] != "match":
                    discrepancies.append({
                        "category": "Table Cell",
                        "field": f"Table {t_idx + 1}, Row {r_idx + 1}: {ocr_col} ↔ {xls_col}",
                        "pdf_value": str(ocr_val) if ocr_val else "",
                        "excel_value": str(xls_val) if xls_val else "",
                        "status": cmp["status"],
                        "reason": cmp["reason"]
                    })
                    if cmp["status"] == "mismatch":
                        mismatch_count += 1
                    else:
                        partial_count += 1
                else:
                    matched_count += 1

    # ---- Unmatched fields / columns ----
    for f in alignment.get("unmatched_ocr", []):
        val = md_data["kv_pairs"].get(f, "")
        if val:
            discrepancies.append({
                "category": "Field Structure",
                "field": f,
                "pdf_value": str(val),
                "excel_value": "(NOT FOUND)",
                "status": "mismatch",
                "reason": f"Field '{f}' exists in PDF but could not be mapped to any Excel field"
            })
            mismatch_count += 1

    for f in alignment.get("unmatched_excel", []):
        val = all_xls_kv.get(f, "")
        if val:
            discrepancies.append({
                "category": "Field Structure",
                "field": f,
                "pdf_value": "(NOT FOUND)",
                "excel_value": str(val),
                "status": "mismatch",
                "reason": f"Field '{f}' exists in Excel but could not be mapped to any PDF field"
            })
            mismatch_count += 1

    return {
        "discrepancies": discrepancies,
        "stats": {
            "matched_fields": matched_count,
            "partial_matches": partial_count,
            "mismatches": mismatch_count,
            "total_differences": len(discrepancies)
        }
    }


# ==========================
# CONSOLE REPORT
# ==========================

def print_report(report):
    """Print a human-readable discrepancy summary."""

    def icon(s):
        return {"partial_match": "⚠️", "mismatch": "❌"}.get(s, "❓")

    print("\n" + "=" * 60)
    print("  DISCREPANCY REPORT: PDF (OCR) vs Excel")
    print("=" * 60)

    discrepancies = report["discrepancies"]
    if not discrepancies:
        print("\n  🎉 Perfect Match! No discrepancies found.")
    else:
        for idx, d in enumerate(discrepancies):
            ic = icon(d["status"])
            print(f"\n  [{idx+1}] {ic} {d['category']}: {d['field']}")
            print(f"      PDF (OCR): {d['pdf_value'] if d['pdf_value'] else '(empty)'}")
            print(f"      Excel:     {d['excel_value'] if d['excel_value'] else '(empty)'}")
            print(f"      → Reason:  {d['reason']}")

    s = report["stats"]
    print("\n" + "=" * 60)
    print(f"  TOTALS:")
    print(f"    ✅ Matched Fields:  {s['matched_fields']}")
    print(f"    ⚠️  Partial Matches: {s['partial_matches']}")
    print(f"    ❌ Mismatches:      {s['mismatches']}")
    print(f"    📊 Total Diff Items: {s['total_differences']}")
    print("=" * 60 + "\n")



# ==========================
# MAIN
# ==========================

def main():
    print("=" * 60)
    print("  SPOTPLAN DISCREPANCY FINDER")
    print("  PDF (via Docling Markdown) vs Excel")
    print("=" * 60)

    # 1. Parse markdown
    print("\n[1/4] Parsing Markdown (OCR)...")
    md_data = parse_markdown(MD_FILE)
    print(f"  KV pairs: {len(md_data['kv_pairs'])}")
    for k, v in md_data["kv_pairs"].items():
        preview = (v[:50] + "...") if len(v) > 50 else v
        print(f"    • {k}: {preview if v else '(empty)'}")
    print(f"  Tables: {len(md_data['tables'])}")
    for i, t in enumerate(md_data["tables"]):
        print(f"    Table {i + 1}: {len(t['headers'])} cols, {len(t['rows'])} rows")
        print(f"      Headers: {t['headers']}")

    # 2. Parse Excel
    print(f"\n[2/4] Parsing Excel...")
    xls_data = parse_excel(XLS_FILE)
    for sheet_name, sheet in xls_data.items():
        print(f"  Sheet: '{sheet_name}'")
        print(f"    KV pairs: {len(sheet['kv_pairs'])}")
        for k, v in sheet["kv_pairs"].items():
            preview = (v[:50] + "...") if len(v) > 50 else v
            print(f"      • {k}: {preview if v else '(empty)'}")
        print(f"    Tables: {len(sheet['tables'])}")
        for i, t in enumerate(sheet["tables"]):
            print(f"      Table {i + 1}: {len(t['headers'])} cols, {len(t['rows'])} rows")
            print(f"        Headers: {t['headers']}")

    # 3. Align fields via LLM
    print(f"\n[3/4] Aligning fields (DeepSeek)...")
    alignment = align_with_llm(md_data, xls_data)

    kvm = alignment.get("kv_mapping", {})
    colm = alignment.get("column_mapping", {})
    print(f"  KV mappings: {len(kvm)}")
    for ok, xk in kvm.items():
        print(f"    {ok}  →  {xk}")
    print(f"  Column mappings: {len(colm)}")
    for oc, xc in colm.items():
        print(f"    {oc}  →  {xc}")
    if alignment.get("unmatched_ocr"):
        print(f"  Unmatched OCR: {alignment['unmatched_ocr']}")
    if alignment.get("unmatched_excel"):
        print(f"  Unmatched Excel: {alignment['unmatched_excel']}")

    # 4. Compare deterministically
    print(f"\n[4/4] Comparing values (deterministic)...")
    report = run_comparison(md_data, xls_data, alignment)

    # Save
    with open("comparison_report.json", "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2, ensure_ascii=False)

    print_report(report)
    print("Saved: comparison_report.json")


if __name__ == "__main__":
    main()