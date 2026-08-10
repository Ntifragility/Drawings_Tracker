from __future__ import annotations

from pathlib import Path
from typing import Any

import pandas as pd

from .models import ComparisonResult, DrawingRecord


def load_excel_records(path: str | Path) -> list[DrawingRecord]:
    import unicodedata
    df = pd.read_excel(path)
    
    def normalize_str(s: str) -> str:
        n = s.strip().lower().replace(" ", "_")
        return "".join(c for c in unicodedata.normalize('NFD', n) if unicodedata.category(c) != 'Mn')
        
    col_map = {normalize_str(str(col)): col for col in df.columns}
    
    def get_val(row, candidates):
        for candidate in candidates:
            norm = normalize_str(candidate)
            if norm in col_map:
                return row[col_map[norm]]
        return None

    records: list[DrawingRecord] = []
    for _, row in df.iterrows():
        records.append(
            DrawingRecord(
                drawing_id=str(get_val(row, ["drawing_id", "Drawing ID", "drawing", "codigo"]) or ""),
                project_code=get_val(row, ["project_code", "Project Code", "project"]),
                revision=get_val(row, ["revision", "Revision", "rev"]),
                status=get_val(row, ["status", "Status", "estado"]),
                file_name=get_val(row, ["file_name", "File Name", "filename"]),
                file_url=get_val(row, ["file_url", "File URL", "url"]),
            )
        )
    return records


def compare_records(current: list[DrawingRecord], previous: list[DrawingRecord]) -> ComparisonResult:
    previous_map = {record.drawing_id: record for record in previous if record.drawing_id}

    new: list[DrawingRecord] = []
    updated: list[DrawingRecord] = []
    unchanged: list[DrawingRecord] = []

    for record in current:
        if not record.drawing_id:
            continue
        prev = previous_map.get(record.drawing_id)
        if prev is None:
            new.append(record)
        elif prev.revision != record.revision:
            updated.append(record)
        else:
            unchanged.append(record)

    return ComparisonResult(new=new, updated=updated, unchanged=unchanged)
