from __future__ import annotations

from dataclasses import dataclass

from .config import MirrorLayout, ReceiverConfig, SiteConfig
from .simulation import annual_samples, summarize_samples


@dataclass(frozen=True)
class Candidate:
    tower_x_m: float
    tower_y_m: float
    width_scale: float
    score_kw_m2: float
    mean_power_mw: float


def scaled_layout(layout: MirrorLayout, width_scale: float) -> MirrorLayout:
    return MirrorLayout(
        mirror_id=layout.mirror_id.copy(),
        x_m=layout.x_m.copy(),
        y_m=layout.y_m.copy(),
        z_m=layout.z_m.copy(),
        width_m=layout.width_m * width_scale,
        height_m=layout.height_m * width_scale,
    )


def grid_search(
    layout: MirrorLayout,
    site: SiteConfig | None = None,
    tower_offsets_m: tuple[float, ...] = (-20.0, 0.0, 20.0),
    width_scales: tuple[float, ...] = (0.9, 1.0, 1.1),
) -> list[Candidate]:
    """Small, deterministic reconstruction example; not the paper's SQP or GA."""
    site = site or SiteConfig()
    candidates: list[Candidate] = []
    for x in tower_offsets_m:
        for y in tower_offsets_m:
            for scale in width_scales:
                candidate_layout = scaled_layout(layout, scale)
                receiver = ReceiverConfig(tower_x_m=x, tower_y_m=y)
                summary = summarize_samples(annual_samples(candidate_layout, site, receiver))
                candidates.append(
                    Candidate(
                        tower_x_m=x,
                        tower_y_m=y,
                        width_scale=scale,
                        score_kw_m2=summary["specific_power_kw_m2"],
                        mean_power_mw=summary["field_power_mw"],
                    )
                )
    return sorted(
        candidates,
        key=lambda item: (-item.score_kw_m2, -item.mean_power_mw, item.tower_x_m, item.tower_y_m),
    )
