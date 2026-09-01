import csv
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_public_samples_are_small_and_schema_stable() -> None:
    expected = ["mirror_id", "width_m", "height_m", "x_m", "y_m", "z_m"]
    for filename in ("result2_sample.csv", "result3_sample.csv"):
        path = ROOT / "data" / "derived" / filename
        with path.open(encoding="utf-8", newline="") as stream:
            rows = list(csv.DictReader(stream))
        assert list(rows[0]) == expected
        assert len(rows) == 96


def test_manifest_states_full_workbooks_are_not_published() -> None:
    path = ROOT / "data" / "derived" / "derivation_manifest.json"
    manifest = json.loads(path.read_text(encoding="utf-8"))
    assert manifest["full_workbooks_published"] is False
    assert len(manifest["summaries"]) == 2
