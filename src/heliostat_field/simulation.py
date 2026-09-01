from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from .config import MirrorLayout, ReceiverConfig, SiteConfig
from .optics import (
    atmospheric_transmittance,
    cosine_efficiency,
    mirror_normals,
    nearest_neighbour_vectors,
    receiver_directions,
    shadow_blocking_efficiency,
    truncation_efficiency,
)
from .solar import direct_normal_irradiance_kw_m2, solar_altitude_rad, sun_vector_enu

SAMPLE_DAYS = np.array([-59, -28, 0, 31, 61, 92, 122, 153, 184, 214, 245, 275], dtype=float)
SAMPLE_TIMES = np.array([9.0, 10.5, 12.0, 13.5, 15.0], dtype=float)


@dataclass(frozen=True)
class SampleResult:
    day_from_equinox: float
    solar_time_hour: float
    altitude_deg: float
    dni_kw_m2: float
    mean_cosine_efficiency: float
    mean_shadow_blocking_efficiency: float
    mean_atmospheric_efficiency: float
    mean_truncation_efficiency: float
    mean_optical_efficiency: float
    field_power_mw: float
    specific_power_kw_m2: float


def evaluate_sample(
    layout: MirrorLayout,
    site: SiteConfig,
    receiver: ReceiverConfig,
    day_from_equinox: float,
    solar_time_hour: float,
    reflectivity: float = 0.92,
    neighbour_cache: tuple[np.ndarray, np.ndarray] | None = None,
) -> SampleResult:
    if not 0.0 < reflectivity <= 1.0:
        raise ValueError("reflectivity must be within (0, 1]")
    sun = sun_vector_enu(site, day_from_equinox, solar_time_hour)
    altitude = solar_altitude_rad(sun)
    dni = direct_normal_irradiance_kw_m2(site, altitude)
    receiver_vectors, distances = receiver_directions(layout, receiver)
    normals = mirror_normals(sun, receiver_vectors)
    eta_cos = cosine_efficiency(sun, normals)
    if neighbour_cache is None:
        neighbour_cache = nearest_neighbour_vectors(layout)
    eta_sb = shadow_blocking_efficiency(
        layout, sun, receiver_vectors, neighbour_cache[0], neighbour_cache[1]
    )
    eta_at = atmospheric_transmittance(distances)
    eta_trunc = truncation_efficiency(distances, receiver.receiver_radius_m)
    eta_optical = reflectivity * eta_cos * eta_sb * eta_at * eta_trunc
    mirror_power_kw = dni * layout.areas_m2 * eta_optical
    total_area = float(np.sum(layout.areas_m2))
    return SampleResult(
        day_from_equinox=day_from_equinox,
        solar_time_hour=solar_time_hour,
        altitude_deg=float(np.rad2deg(altitude)),
        dni_kw_m2=dni,
        mean_cosine_efficiency=float(np.average(eta_cos, weights=layout.areas_m2)),
        mean_shadow_blocking_efficiency=float(np.average(eta_sb, weights=layout.areas_m2)),
        mean_atmospheric_efficiency=float(np.average(eta_at, weights=layout.areas_m2)),
        mean_truncation_efficiency=float(np.average(eta_trunc, weights=layout.areas_m2)),
        mean_optical_efficiency=float(np.average(eta_optical, weights=layout.areas_m2)),
        field_power_mw=float(np.sum(mirror_power_kw) / 1000.0),
        specific_power_kw_m2=float(np.sum(mirror_power_kw) / total_area),
    )


def annual_samples(
    layout: MirrorLayout,
    site: SiteConfig | None = None,
    receiver: ReceiverConfig | None = None,
) -> list[SampleResult]:
    site = site or SiteConfig()
    receiver = receiver or ReceiverConfig()
    neighbour_cache = nearest_neighbour_vectors(layout)
    return [
        evaluate_sample(layout, site, receiver, day, time, neighbour_cache=neighbour_cache)
        for day in SAMPLE_DAYS
        for time in SAMPLE_TIMES
    ]


def summarize_samples(samples: list[SampleResult]) -> dict[str, float]:
    if not samples:
        raise ValueError("samples must not be empty")
    keys = (
        "mean_cosine_efficiency",
        "mean_shadow_blocking_efficiency",
        "mean_atmospheric_efficiency",
        "mean_truncation_efficiency",
        "mean_optical_efficiency",
        "field_power_mw",
        "specific_power_kw_m2",
    )
    return {key: float(np.mean([getattr(sample, key) for sample in samples])) for key in keys}
