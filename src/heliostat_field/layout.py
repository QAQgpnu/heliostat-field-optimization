from __future__ import annotations

import csv
from pathlib import Path

import numpy as np

from .config import MirrorLayout

PUBLIC_COLUMNS = ("mirror_id", "width_m", "height_m", "x_m", "y_m", "z_m")


def load_layout_csv(path: str | Path) -> MirrorLayout:
    source = Path(path)
    with source.open("r", encoding="utf-8-sig", newline="") as stream:
        rows = list(csv.DictReader(stream))
    if not rows:
        raise ValueError(f"layout CSV is empty: {source}")
    missing = set(PUBLIC_COLUMNS) - set(rows[0])
    if missing:
        raise ValueError(f"missing columns: {sorted(missing)}")
    return MirrorLayout(
        mirror_id=np.array([int(row["mirror_id"]) for row in rows]),
        width_m=np.array([float(row["width_m"]) for row in rows]),
        height_m=np.array([float(row["height_m"]) for row in rows]),
        x_m=np.array([float(row["x_m"]) for row in rows]),
        y_m=np.array([float(row["y_m"]) for row in rows]),
        z_m=np.array([float(row["z_m"]) for row in rows]),
    )


def generate_ring_layout(
    rings: int = 5,
    mirrors_per_ring: int = 36,
    inner_radius_m: float = 110.0,
    ring_spacing_m: float = 22.0,
    width_m: float = 4.0,
    height_m: float = 5.0,
    center_height_m: float = 4.0,
) -> MirrorLayout:
    if rings <= 0 or mirrors_per_ring <= 2:
        raise ValueError("rings and mirrors_per_ring must be positive and non-degenerate")
    x_values: list[float] = []
    y_values: list[float] = []
    for ring in range(rings):
        count = mirrors_per_ring + ring * 4
        radius = inner_radius_m + ring * ring_spacing_m
        angles = np.linspace(0.0, 2.0 * np.pi, count, endpoint=False) + (ring % 2) * np.pi / count
        x_values.extend((radius * np.cos(angles)).tolist())
        y_values.extend((radius * np.sin(angles)).tolist())
    count = len(x_values)
    return MirrorLayout(
        mirror_id=np.arange(1, count + 1),
        x_m=np.array(x_values),
        y_m=np.array(y_values),
        z_m=np.full(count, center_height_m),
        width_m=np.full(count, width_m),
        height_m=np.full(count, height_m),
    )
