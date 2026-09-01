import csv
from pathlib import Path

import numpy as np
import pytest

from heliostat_field.config import MirrorLayout, SiteConfig
from heliostat_field.layout import generate_ring_layout, load_layout_csv
from heliostat_field.optimization import grid_search
from heliostat_field.simulation import annual_samples, summarize_samples


def test_layout_validation_rejects_mismatched_arrays() -> None:
    with pytest.raises(ValueError):
        MirrorLayout(
            mirror_id=np.array([1, 2]),
            x_m=np.array([1.0]),
            y_m=np.array([1.0, 2.0]),
            z_m=np.array([3.0, 3.0]),
            width_m=np.array([4.0, 4.0]),
            height_m=np.array([5.0, 5.0]),
        )


def test_csv_round_trip_load(tmp_path: Path) -> None:
    path = tmp_path / "layout.csv"
    with path.open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(
            stream, fieldnames=["mirror_id", "width_m", "height_m", "x_m", "y_m", "z_m"]
        )
        writer.writeheader()
        writer.writerow(
            {"mirror_id": 1, "width_m": 4, "height_m": 5, "x_m": 110, "y_m": 0, "z_m": 4}
        )
    layout = load_layout_csv(path)
    assert len(layout) == 1
    assert layout.areas_m2[0] == pytest.approx(20.0)


def test_annual_sampling_has_60_points_and_physical_bounds() -> None:
    layout = generate_ring_layout(rings=2, mirrors_per_ring=10)
    results = annual_samples(layout)
    summary = summarize_samples(results)
    assert len(results) == 60
    assert 0.0 < summary["mean_optical_efficiency"] <= 1.0
    assert summary["field_power_mw"] > 0.0
    assert summary["specific_power_kw_m2"] > 0.0


def test_grid_search_is_reproducible() -> None:
    layout = generate_ring_layout(rings=1, mirrors_per_ring=8)
    first = grid_search(layout, SiteConfig(), tower_offsets_m=(0.0, 10.0), width_scales=(1.0,))
    second = grid_search(layout, SiteConfig(), tower_offsets_m=(0.0, 10.0), width_scales=(1.0,))
    assert first == second
    assert len(first) == 4
    assert first[0].score_kw_m2 >= first[-1].score_kw_m2
