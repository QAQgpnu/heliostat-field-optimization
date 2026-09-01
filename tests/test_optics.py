import numpy as np
import pytest

from heliostat_field.config import ReceiverConfig, SiteConfig
from heliostat_field.layout import generate_ring_layout
from heliostat_field.optics import (
    atmospheric_transmittance,
    cosine_efficiency,
    mirror_normals,
    receiver_directions,
    shadow_blocking_efficiency,
    truncation_efficiency,
)
from heliostat_field.solar import sun_vector_enu


def test_reflection_bisector_has_valid_cosine() -> None:
    layout = generate_ring_layout(rings=1, mirrors_per_ring=8)
    receiver_vectors, _ = receiver_directions(layout, ReceiverConfig())
    sun = sun_vector_enu(SiteConfig(), 0.0, 12.0)
    normals = mirror_normals(sun, receiver_vectors)
    eta = cosine_efficiency(sun, normals)
    assert np.all((eta >= 0.0) & (eta <= 1.0))
    assert np.allclose(np.linalg.norm(normals, axis=1), 1.0)


def test_atmospheric_transmittance_is_bounded() -> None:
    eta = atmospheric_transmittance(np.array([100.0, 500.0, 1000.0]))
    assert np.all((eta >= 0.0) & (eta <= 1.0))
    assert eta[0] > eta[-1]


def test_truncation_decreases_with_distance() -> None:
    eta = truncation_efficiency(np.array([100.0, 200.0, 400.0]), 3.5)
    assert eta[0] > eta[1] > eta[2]


def test_shadow_proxy_is_bounded_and_deterministic() -> None:
    layout = generate_ring_layout(rings=2, mirrors_per_ring=10)
    receiver_vectors, _ = receiver_directions(layout, ReceiverConfig())
    sun = sun_vector_enu(SiteConfig(), 0.0, 10.5)
    first = shadow_blocking_efficiency(layout, sun, receiver_vectors)
    second = shadow_blocking_efficiency(layout, sun, receiver_vectors)
    assert first == pytest.approx(second)
    assert np.all((first >= 0.35) & (first <= 1.0))
