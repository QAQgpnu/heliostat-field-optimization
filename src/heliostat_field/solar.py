from __future__ import annotations

import numpy as np

from .config import SiteConfig


def solar_declination_rad(day_from_spring_equinox: float) -> float:
    """Return the contest-style solar declination approximation in radians."""
    axial_tilt = np.deg2rad(23.45)
    return float(
        np.arcsin(np.sin(2.0 * np.pi * day_from_spring_equinox / 365.0) * np.sin(axial_tilt))
    )


def solar_hour_angle_rad(local_solar_time_hour: float) -> float:
    if not 0.0 <= local_solar_time_hour <= 24.0:
        raise ValueError("local_solar_time_hour must be within [0, 24]")
    return float(np.pi * (local_solar_time_hour - 12.0) / 12.0)


def sun_vector_enu(
    site: SiteConfig,
    day_from_spring_equinox: float,
    local_solar_time_hour: float,
) -> np.ndarray:
    """Unit vector from a mirror toward the Sun in east-north-up coordinates."""
    latitude = np.deg2rad(site.latitude_deg)
    declination = solar_declination_rad(day_from_spring_equinox)
    hour_angle = solar_hour_angle_rad(local_solar_time_hour)
    vector = np.array(
        [
            -np.cos(declination) * np.sin(hour_angle),
            np.sin(declination) * np.cos(latitude)
            - np.cos(declination) * np.sin(latitude) * np.cos(hour_angle),
            np.sin(declination) * np.sin(latitude)
            + np.cos(declination) * np.cos(latitude) * np.cos(hour_angle),
        ]
    )
    norm = np.linalg.norm(vector)
    if norm == 0.0 or vector[2] <= 0.0:
        raise ValueError("Sun is below the horizon for this sample")
    return vector / norm


def solar_altitude_rad(sun_vector: np.ndarray) -> float:
    vector = np.asarray(sun_vector, dtype=float)
    if vector.shape != (3,):
        raise ValueError("sun_vector must have shape (3,)")
    return float(np.arcsin(np.clip(vector[2] / np.linalg.norm(vector), -1.0, 1.0)))


def direct_normal_irradiance_kw_m2(site: SiteConfig, altitude_rad: float) -> float:
    """DNI approximation supplied with the 2023 CUMCM A problem."""
    if altitude_rad <= 0.0:
        return 0.0
    altitude = site.altitude_km
    a = 0.4237 - 0.00821 * (6.0 - altitude) ** 2
    b = 0.5055 + 0.00595 * (6.5 - altitude) ** 2
    c = 0.2711 + 0.01858 * (2.5 - altitude) ** 2
    solar_constant_kw_m2 = 1.366
    return float(solar_constant_kw_m2 * (a + b * np.exp(-c / np.sin(altitude_rad))))
