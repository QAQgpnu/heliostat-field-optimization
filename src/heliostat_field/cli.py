from __future__ import annotations

import argparse
import csv
import json
from dataclasses import asdict
from pathlib import Path

import matplotlib
import numpy as np

matplotlib.use("Agg")
import matplotlib.pyplot as plt

from .config import ReceiverConfig, SiteConfig
from .layout import generate_ring_layout, load_layout_csv
from .optimization import grid_search
from .simulation import annual_samples, summarize_samples

DEFAULT_RANDOM_SEED = 20230910


def _monthly_means(samples: list) -> list[dict[str, float]]:
    result = []
    for month_index in range(12):
        group = samples[month_index * 5 : (month_index + 1) * 5]
        result.append(
            {
                "month": month_index + 1,
                "optical_efficiency": float(
                    np.mean([item.mean_optical_efficiency for item in group])
                ),
                "cosine_efficiency": float(
                    np.mean([item.mean_cosine_efficiency for item in group])
                ),
                "shadow_blocking_efficiency": float(
                    np.mean([item.mean_shadow_blocking_efficiency for item in group])
                ),
                "specific_power_kw_m2": float(
                    np.mean([item.specific_power_kw_m2 for item in group])
                ),
            }
        )
    return result


def _save_monthly_plot(monthly: list[dict[str, float]], destination: Path) -> None:
    months = [item["month"] for item in monthly]
    fig, (left, right) = plt.subplots(1, 2, figsize=(11, 4.2))
    left.plot(months, [item["optical_efficiency"] for item in monthly], marker="o", label="Optical")
    left.plot(months, [item["cosine_efficiency"] for item in monthly], marker="s", label="Cosine")
    left.plot(
        months,
        [item["shadow_blocking_efficiency"] for item in monthly],
        marker="^",
        label="Shadow/blocking proxy",
    )
    left.set(xlabel="Month", ylabel="Efficiency", title="Reconstructed monthly efficiencies")
    left.set_xticks(months)
    left.set_ylim(0.0, 1.05)
    left.grid(alpha=0.25)
    left.legend(fontsize=8)
    right.bar(months, [item["specific_power_kw_m2"] for item in monthly], color="#d97706")
    right.set(xlabel="Month", ylabel="kW/m2", title="Specific thermal power at sample times")
    right.set_xticks(months)
    right.grid(axis="y", alpha=0.25)
    fig.tight_layout()
    fig.savefig(destination, dpi=180)
    plt.close(fig)


def _save_layout_plot(result2_path: Path, result3_path: Path, destination: Path) -> None:
    layouts = [load_layout_csv(result2_path), load_layout_csv(result3_path)]
    fig, axes = plt.subplots(1, 2, figsize=(10, 4.6), sharex=True, sharey=True)
    for axis, layout, title in zip(
        axes, layouts, ("Retained result2 sample", "Retained result3 sample")
    ):
        points = axis.scatter(layout.x_m, layout.y_m, c=layout.areas_m2, s=20, cmap="viridis")
        axis.set(xlabel="East x (m)", ylabel="North y (m)", title=title)
        axis.set_aspect("equal")
        axis.grid(alpha=0.2)
        fig.colorbar(points, ax=axis, label="Mirror area (m2)")
    fig.suptitle("Deterministic 96-row samples; not the complete retained workbooks", fontsize=10)
    fig.tight_layout()
    fig.savefig(destination, dpi=180)
    plt.close(fig)


def _save_optimization_plot(candidates: list, destination: Path) -> None:
    fig, axis = plt.subplots(figsize=(7, 4.5))
    scatter = axis.scatter(
        [item.mean_power_mw for item in candidates],
        [item.score_kw_m2 for item in candidates],
        c=[item.width_scale for item in candidates],
        cmap="plasma",
        s=50,
    )
    best = candidates[0]
    axis.scatter(
        [best.mean_power_mw],
        [best.score_kw_m2],
        marker="*",
        s=180,
        color="#111827",
        label="Best grid score",
    )
    axis.set(
        xlabel="Mean field power (MW)",
        ylabel="Mean specific power (kW/m2)",
        title="Small deterministic grid-search reconstruction",
    )
    axis.grid(alpha=0.25)
    axis.legend()
    fig.colorbar(scatter, ax=axis, label="Mirror dimension scale")
    fig.tight_layout()
    fig.savefig(destination, dpi=180)
    plt.close(fig)


def run_demo(output_dir: Path, data_dir: Path) -> dict:
    np.random.seed(DEFAULT_RANDOM_SEED)
    output_dir.mkdir(parents=True, exist_ok=True)
    layout = generate_ring_layout()
    site = SiteConfig()
    receiver = ReceiverConfig()
    samples = annual_samples(layout, site, receiver)
    summary = summarize_samples(samples)
    monthly = _monthly_means(samples)
    candidates = grid_search(layout, site)
    best = candidates[0]
    payload = {
        "model_status": "reconstruction with documented approximations",
        "random_seed": DEFAULT_RANDOM_SEED,
        "synthetic_demo_mirror_count": len(layout),
        "annual_sample_count": len(samples),
        "summary": summary,
        "best_grid_candidate": asdict(best),
        "paper_values_are_not_validation_targets": True,
    }
    (output_dir / "demo_summary.json").write_text(
        json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    with (output_dir / "monthly_summary.csv").open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(monthly[0]))
        writer.writeheader()
        writer.writerows(monthly)
    _save_monthly_plot(monthly, output_dir / "monthly_efficiency.png")
    _save_optimization_plot(candidates, output_dir / "optimization_candidates.png")
    result2 = data_dir / "result2_sample.csv"
    result3 = data_dir / "result3_sample.csv"
    if result2.exists() and result3.exists():
        _save_layout_plot(result2, result3, output_dir / "layout_comparison.png")
    return payload


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run the documented heliostat reconstruction demo")
    parser.add_argument("--output-dir", type=Path, default=Path("artifacts/demo"))
    parser.add_argument("--data-dir", type=Path, default=Path("data/derived"))
    return parser


def main() -> None:
    args = build_parser().parse_args()
    payload = run_demo(args.output_dir, args.data_dir)
    print(json.dumps(payload, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
