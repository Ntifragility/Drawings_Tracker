from pathlib import Path

import pandas as pd

from drawings_tracker.core import DrawingTracker


def test_compare_status_files_detects_new_and_updated_drawings(tmp_path: Path) -> None:
    previous = tmp_path / "previous.xlsx"
    latest = tmp_path / "latest.xlsx"

    previous_df = pd.DataFrame([
        {"drawing_id": "1001", "revision": "A", "status": "Pending"},
        {"drawing_id": "1002", "revision": "B", "status": "Approved"},
    ])
    latest_df = pd.DataFrame([
        {"drawing_id": "1001", "revision": "B", "status": "Pending"},
        {"drawing_id": "1003", "revision": "A", "status": "New"},
    ])

    previous_df.to_excel(previous, index=False)
    latest_df.to_excel(latest, index=False)

    tracker = DrawingTracker(data_dir=tmp_path)
    changes = tracker.compare_status_files(previous, latest)

    assert len(changes["updated_drawings"]) == 1
    assert changes["updated_drawings"][0]["drawing_id"] == "1001"
    assert len(changes["new_drawings"]) == 1
    assert changes["new_drawings"][0]["drawing_id"] == "1003"
