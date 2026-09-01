from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path

import numpy as np
import openpyxl

PUBLIC_FIELDS = ("mirror_id", "width_m", "height_m", "x_m", "y_m", "z_m")


def read_retained_workbook(path: Path) -> tuple[dict[str, float], list[dict[str, float]]]:
    workbook = openpyxl.load_workbook(path, read_only=True, data_only=True)
    worksheet = workbook.active
    rows = list(worksheet.iter_rows(min_row=2, values_only=True))
    if not rows:
        raise ValueError(f"no data rows in {path}")
    tower = {"tower_x_m": float(rows[0][0]), "tower_y_m": float(rows[0][1])}
    records = []
    for row in rows:
        records.append(
            {
                "mirror_id": int(row[2]),
                "width_m": float(row[3]),
                "height_m": float(row[4]),
                "x_m": float(row[5]),
                "y_m": float(row[6]),
                "z_m": float(row[7]),
            }
        )
    return tower, records


def summarize(
    name: str, tower: dict[str, float], rows: list[dict[str, float]]
) -> dict[str, float | str]:
    width = np.array([row["width_m"] for row in rows])
    height = np.array([row["height_m"] for row in rows])
    x = np.array([row["x_m"] for row in rows])
    y = np.array([row["y_m"] for row in rows])
    radius = np.hypot(x - tower["tower_x_m"], y - tower["tower_y_m"])
    field_center_radius = np.hypot(x, y)
    xy = np.column_stack([x, y])
    delta = xy[None, :, :] - xy[:, None, :]
    distance = np.linalg.norm(delta, axis=2)
    np.fill_diagonal(distance, np.inf)
    nearest_spacing = np.min(distance, axis=1)
    area = width * height
    return {
        "layout": name,
        "retained_rows": len(rows),
        **tower,
        "width_min_m": float(width.min()),
        "width_mean_m": float(width.mean()),
        "width_max_m": float(width.max()),
        "height_min_m": float(height.min()),
        "height_mean_m": float(height.mean()),
        "height_max_m": float(height.max()),
        "mirror_area_total_m2": float(area.sum()),
        "radius_min_m": float(radius.min()),
        "radius_mean_m": float(radius.mean()),
        "radius_max_m": float(radius.max()),
        "field_center_radius_min_m": float(field_center_radius.min()),
        "field_center_radius_max_m": float(field_center_radius.max()),
        "mirrors_within_100m_of_tower": int(np.count_nonzero(radius < 100.0)),
        "nearest_spacing_min_m": float(nearest_spacing.min()),
        "spacing_violations_vs_width_plus_5m": int(
            np.count_nonzero(nearest_spacing < width + 5.0 - 1e-9)
        ),
    }


def deterministic_sample(rows: list[dict[str, float]], count: int) -> list[dict[str, float]]:
    if count <= 0:
        raise ValueError("sample count must be positive")
    indices = np.linspace(0, len(rows) - 1, min(count, len(rows)), dtype=int)
    return [rows[int(index)] for index in indices]


def write_csv(path: Path, rows: list[dict], fields: tuple[str, ...] | list[str]) -> None:
    with path.open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(fields))
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Create a small public derivative from retained team workbooks"
    )
    parser.add_argument("result2", type=Path)
    parser.add_argument("result3", type=Path)
    parser.add_argument("output_dir", type=Path)
    parser.add_argument("--sample-count", type=int, default=96)
    args = parser.parse_args()
    args.output_dir.mkdir(parents=True, exist_ok=True)
    summaries = []
    for name, source in (("result2", args.result2), ("result3", args.result3)):
        tower, rows = read_retained_workbook(source)
        summaries.append(summarize(name, tower, rows))
        sample = deterministic_sample(rows, args.sample_count)
        write_csv(args.output_dir / f"{name}_sample.csv", sample, PUBLIC_FIELDS)
    write_csv(args.output_dir / "layout_comparison_summary.csv", summaries, list(summaries[0]))
    manifest = {
        "status": "derived from retained team-result workbooks",
        "sampling": "96 evenly spaced row indices including first and last; no random selection",
        "full_workbooks_published": False,
        "summaries": summaries,
    }
    (args.output_dir / "derivation_manifest.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )


if __name__ == "__main__":
    main()
