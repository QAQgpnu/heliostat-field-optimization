import numpy as np
import pytest

from heliostat_field.config import SiteConfig
from heliostat_field.solar import (
    direct_normal_irradiance_kw_m2,
    solar_altitude_rad,
    solar_declination_rad,
    solar_hour_angle_rad,
    sun_vector_enu,
)


def test_equinox_declination_is_zero() -> None:
    assert solar_declination_rad(0.0) == pytest.approx(0.0, abs=1e-12)


def test_noon_hour_angle_is_zero() -> None:
    assert solar_hour_angle_rad(12.0) == pytest.approx(0.0)


def test_sun_vector_is_unit_and_above_horizon() -> None:
    vector = sun_vector_enu(SiteConfig(), 0.0, 12.0)
    assert np.linalg.norm(vector) == pytest.approx(1.0)
    assert vector[2] > 0.0


def test_morning_and_afternoon_have_opposite_east_components() -> None:
    site = SiteConfig()
    morning = sun_vector_enu(site, 0.0, 9.0)
    afternoon = sun_vector_enu(site, 0.0, 15.0)
    assert morning[0] == pytest.approx(-afternoon[0])
    assert morning[1:] == pytest.approx(afternoon[1:])


def test_dni_positive_at_sample_time() -> None:
    site = SiteConfig()
    sun = sun_vector_enu(site, 0.0, 12.0)
    dni = direct_normal_irradiance_kw_m2(site, solar_altitude_rad(sun))
    assert 0.0 < dni < 1.366


def test_invalid_time_rejected() -> None:
    with pytest.raises(ValueError):
        solar_hour_angle_rad(25.0)
